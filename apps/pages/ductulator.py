# apps/pages/ductulator.py
from dash import register_page, html, dcc, Input, Output, State, callback, no_update
from apps.shared.ui import BRAND, MUTED, BLACK, section_card, input_box
import math

register_page(__name__, path="/ductulator", name="Ductulator")

# ------------------ Physics helpers ------------------
RHO_AIR = 1.2     # kg/m^3 @ ~20°C
MU_AIR  = 1.8e-5  # Pa·s   @ ~20°C

ROUGHNESS_PRESETS = {
    "Galvanized steel (0.15 mm)": 0.00015,
    "Spiral steel (0.09 mm)":     0.00009,
    "Flexible duct (~1.0 mm)":    0.00100,
    "Custom…":                    None,
}

def area_m2(shape: str, a_mm: float, b_mm: float | None = None) -> float:
    if shape == "circular":
        D = (a_mm or 0.0) / 1000.0
        return math.pi * (D**2) / 4.0
    a = (a_mm or 0.0) / 1000.0
    b = (b_mm or 0.0) / 1000.0
    return a * b

def equiv_diameter_m(shape: str, a_mm: float, b_mm: float | None = None) -> float:
    if shape == "circular":
        return (a_mm or 0.0) / 1000.0
    a = (a_mm or 0.0) / 1000.0
    b = (b_mm or 0.0) / 1000.0
    if a + b == 0:
        return 0.0
    # ASHRAE equal-friction equivalent diameter
    return 1.30 * (a * b) ** 0.625 / (a + b) ** 0.25

def velocity_ms(flow_ls: float, area: float) -> float:
    Q = (flow_ls or 0.0) / 1000.0  # m³/s
    return 0.0 if area <= 0 else Q / area

def swamee_jain_f(Re: float, eps: float, D: float) -> float:
    if Re <= 0 or D <= 0: return 0.0
    if Re < 2000.0: return 64.0 / Re
    term = (eps / (3.7 * D)) + (5.74 / (Re ** 0.9))
    return 0.25 / (math.log10(term) ** 2)

def duct_drop(flow_ls: float, area: float, D: float, *, eps=0.00015, rho=RHO_AIR, mu=MU_AIR, L=1.0):
    """Return (Pa_per_m, Pa_total, V, Re, f) for straight duct."""
    V  = velocity_ms(flow_ls, area)
    Re = 0.0 if V == 0 else rho * V * D / mu
    f  = swamee_jain_f(Re, eps, D)
    pa_per_m = 0.0 if D == 0 else f * (rho * V * V) / (2.0 * D)
    return pa_per_m, pa_per_m * L, V, Re, f

# ------------------ UI helpers ------------------
ROW_STYLE = {
    "display": "grid",
    "gridTemplateColumns": "240px 220px 120px",  # label | input | unit
    "columnGap": "14px",
    "rowGap": "10px",
    "alignItems": "center",
    "maxWidth": "820px",
}
SHOW_ROW_STYLE = {**ROW_STYLE, "marginBottom": "10px"}
HIDE_ROW_STYLE = {**SHOW_ROW_STYLE, "display": "none"}

def label_with_hint(title: str, hint: str, _id: str | None = None):
    children = [
        html.Div(title, style={"fontWeight": 600}),
        html.Div(hint,  style={"fontSize": "12px", "color": "#666"}),
    ]
    return html.Div(children, **({"id": _id} if _id is not None else {}))

def form_row(label_comp, control_comp, unit_text: str, row_id: str | None = None) -> html.Div:
    props = {"style": SHOW_ROW_STYLE, "children": [label_comp, control_comp, html.Div(unit_text)]}
    if row_id is not None:
        props["id"] = row_id
    return html.Div(**props)

# ------------------ Layout ------------------
layout = html.Div(
    style={"width": "100%", "padding": "16px", "fontFamily": "Segoe UI, Inter, Arial", "color": BLACK},
    children=[
        html.H2("Ductulator"),
        dcc.Markdown("Compute **velocity** and **friction loss** for circular or rectangular ducts (SI units)."),

        form_row(html.Div(html.B("Flow (L/s)")),
                 dcc.Input(id="du-flow", type="number", value=600, step=10, style={"width": "200px"}), ""),

        form_row(html.Div(html.B("Shape")),
                 dcc.Dropdown(id="du-shape",
                              options=[{"label": "Circular", "value": "circular"},
                                       {"label": "Rectangular", "value": "rectangular"}],
                              value="circular", clearable=False, style={"width": "200px"}), ""),

        # Circular only
        form_row(html.Div(html.B("Diameter (mm)")),
                 dcc.Input(id="du-diam", type="number", value=350, step=5, style={"width": "200px"}), "mm",
                 row_id="row-diam"),

        # Rectangular only
        form_row(label_with_hint("Width (mm)", "shown when rectangular"),
                 dcc.Input(id="du-width", type="number", value=400, step=5, style={"width": "200px"}), "mm",
                 row_id="row-width"),
        form_row(html.Div(html.B("Height (mm)")),
                 dcc.Input(id="du-height", type="number", value=250, step=5, style={"width": "200px"}), "mm",
                 row_id="row-height"),

        form_row(html.Div(html.B("Length (m)")),
                 dcc.Input(id="du-length", type="number", value=10.0, step=0.5, style={"width": "200px"}), ""),

        form_row(html.Div(html.B("Wall roughness")),
                 dcc.Dropdown(id="du-rough-preset",
                              options=[{"label": k, "value": k} for k in ROUGHNESS_PRESETS],
                              value="Galvanized steel (0.15 mm)", clearable=False, style={"width": "200px"}), ""),

        form_row(html.Div(html.B("Custom roughness ε")),
                 dcc.Input(id="du-rough-custom", type="number", value=0.15, step=0.01, style={"width": "200px"}), "mm", row_id="row-rough-custom",),

        html.Button("Calculate", id="du-calc", n_clicks=0,
                    style={"padding": "8px 14px", "borderRadius": "8px", "border": "1px solid #ccc",
                           "background": "#f7f7f7", "marginTop": "8px"}),

        html.Div(id="du-results",
                 style={"marginTop": "16px", "padding": "14px", "border": "1px solid #e5e5e5",
                        "borderRadius": "10px", "maxWidth": "820px", "background": "#fafafa", "lineHeight": "1.6"}),

        html.H2("Pressure Calculation"),
        dcc.Markdown("Compute **fitting pressure loss**."),

        section_card(
            "Pressure Calculation",
            [],
            [
                html.Div(
                    dcc.Markdown(
                        r"$$\Delta p = K\,p_v,\qquad p_v=\tfrac{1}{2}\rho v^2$$",
                        mathjax=True,
                        style={"textAlign": "center", "width": "100%", "marginBottom": "12px"},
                    ),
                    style={"width": "100%"},
                ),
                html.Div([html.Label("Velocity v (m/s)"),
                          input_box("vel-kvp", 3.5, step=0.1, width="140px")],
                         style={"display": "flex", "flexDirection": "column"}),
                html.Div([html.Label("Loss coefficient K (–)"),
                          input_box("k-kvp", 0.17, step=0.01, width="140px")],
                         style={"display": "flex", "flexDirection": "column"}),
            ],
            result_id="pressure-kvp",
        ),
    ],
)

# ------------------ Show/Hide rows so columns stay aligned ------------------
@callback(
    Output("row-diam", "style"),
    Output("row-width", "style"),
    Output("row-height", "style"),
    Input("du-shape", "value"),
)
def toggle_shape_rows(shape):
    if shape == "circular":
        return SHOW_ROW_STYLE, HIDE_ROW_STYLE, HIDE_ROW_STYLE
    return HIDE_ROW_STYLE, SHOW_ROW_STYLE, SHOW_ROW_STYLE

# ------------------ Compute helpers ------------------
def calc_pressure_loss(v, k):
    if v is None or k is None:
        return ""

    rho = RHO_AIR  # constant air density
    v = float(v)
    k = float(k)

    vp = 0.5 * rho * v * v
    dp = k * vp
    subtle = {"color": "#666", "marginLeft": "6px"}

    return html.Div(
        [
            html.Div([
                html.B("Velocity pressure = "),
                html.Strong(f"{vp:,.2f} Pa"),
                html.Span(f" ({vp/1000:.3f} kPa)", style=subtle),
            ]),
            html.Div([
                html.B("Fitting loss = "),
                html.Strong(f"{dp:,.2f} Pa"),
                html.Span(f" ({dp/1000:.3f} kPa)", style=subtle),
            ]),
        ],
        style={"lineHeight": "1.6", "margin": 0}
    )

# ------------------ Ductulator (button-triggered) ------------------
# Also writes the computed velocity into the pressure card's velocity input.
@callback(
    Output("du-results", "children"),
    Output("vel-kvp", "value"),
    Input("du-calc", "n_clicks"),
    State("du-flow", "value"),
    State("du-shape", "value"),
    State("du-diam", "value"),
    State("du-width", "value"),
    State("du-height", "value"),
    State("du-length", "value"),
    State("du-rough-preset", "value"),
    State("du-rough-custom", "value"),
    prevent_initial_call=True,
)

def compute_ductulator(n_clicks,
                       flow_ls, shape, diam_mm, width_mm, height_mm, length_m,
                       rough_preset, rough_custom_mm):

    # Validate basics
    try:
        flow_ls = float(flow_ls or 0)
        length_m = float(length_m or 0)
    except Exception:
        return "Please enter valid numeric values.", no_update
    
    rho = RHO_AIR
    mu  = MU_AIR

    # Geometry
    if shape == "circular":
        if not diam_mm:
            return "Enter a diameter.", no_update
        A = area_m2("circular", float(diam_mm))
        D = equiv_diameter_m("circular", float(diam_mm))
        dims_label = f"Ø {float(diam_mm):.0f} mm"
    else:
        if not (width_mm and height_mm):
            return "Enter width and height.", no_update
        A = area_m2("rectangular", float(width_mm), float(height_mm))
        D = equiv_diameter_m("rectangular", float(width_mm), float(height_mm))
        dims_label = f"{float(width_mm):.0f} × {float(height_mm):.0f} mm"

    # Roughness selection (convert custom mm -> m)
    eps = ROUGHNESS_PRESETS.get(rough_preset)
    if eps is None:
        try:
            eps = (float(rough_custom_mm) or 0.0) / 1000.0
        except Exception:
            eps = 0.00015

    # Calculations
    pa_m, pa_total, V, Re, f = duct_drop(flow_ls, A, D, eps=eps, rho=rho, mu=mu, L=length_m)
    VP = 0.5 * rho * V * V

    def fmt(v, unit="", d=3):
        try:
            return f"{v:.{d}f} {unit}".rstrip()
        except Exception:
            return str(v)

    duct_div = html.Div([
        html.Div([html.B("Inputs")]),
        html.Ul([
            html.Li(f"Flow: {fmt(flow_ls, 'L/s', 1)}"),
            html.Li(f"Shape & size: {dims_label}"),
            html.Li(f"Length: {fmt(length_m, 'm', 2)}"),
            html.Li(f"Roughness ε: {fmt(eps*1000, 'mm', 3)} ({rough_preset})"),
            html.Li(f"Air properties: ρ: {fmt(rho, 'kg/m³', 3)}   •   μ: {mu:g} Pa·s"),
        ]),
        html.Hr(),
        html.Div([html.B("Results")]),
        html.Ul([
            html.Li(f"Area A: {fmt(A, 'm²', 4)}"),
            html.Li(f"Equivalent diameter Dₑ: {fmt(D*1000, 'mm', 1)}"),
            html.Li(f"Velocity V: {fmt(V, 'm/s', 3)}"),
            html.Li(f"Reynolds number Re: {Re:,.0f}"),
            html.Li(f"Friction factor f: {fmt(f, '', 5)}"),
            html.Li(f"Velocity pressure VP = ½ρV²: {fmt(VP, 'Pa', 2)}"),
            html.Li(f"Friction rate Δp/L: {fmt(pa_m, 'Pa/m', 3)}"),
            html.Li(f"Total straight loss Δp = (Δp/L)·L: {fmt(pa_total, 'Pa', 2)}"),
        ]),
        html.Div("Note: straight-duct result only. Add fitting losses separately using K·VP."),
    ])

    # Return results and set the velocity field for the pressure card
    return duct_div, round(V, 3)

# ------------------ Pressure calc (live) ------------------
# Live update as ρ, v, or K changes (no button needed)
@callback(
    Output("pressure-kvp", "children"),
    Input("vel-kvp", "value"),
    Input("k-kvp", "value"),
)
def live_pressure(v_kvp, k_kvp):
    return calc_pressure_loss(v_kvp, k_kvp)

# Show the custom roughness input row ONLY when "Custom…" roughness is selected.
# This keeps the UI clean and prevents users from entering unused values.
@callback(
    Output("row-rough-custom", "style"),
    Input("du-rough-preset", "value"),
)
def toggle_custom_roughness(preset):
    if preset == "Custom…":
        return SHOW_ROW_STYLE
    return HIDE_ROW_STYLE