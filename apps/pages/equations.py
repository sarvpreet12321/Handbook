# apps/pages/equations.py
from dash import register_page, html, dcc, Input, Output, dash_table, callback
from apps.shared.ui import section_card, input_box, dropdown, BRAND, MUTED, BLACK

register_page(__name__, path="/equations", name="Equations")

# --- Abbreviations table data ---
abbr_rows = [
    {"Symbol": "Q",     "Meaning": "Air Flow",                 "Units": "L/s"},
    {"Symbol": "v",     "Meaning": "Air Velocity",             "Units": "m/s"},
    {"Symbol": "A",     "Meaning": "Area",                     "Units": "m²"},
    {"Symbol": "V",     "Meaning": "Volume",                   "Units": "m³"},
    {"Symbol": "ΔT",    "Meaning": "Temperature Difference",   "Units": "°C"},
    {"Symbol": "g/kg",  "Meaning": "Moisture Content",         "Units": "Refer to Psychrometric Chart"},
    {"Symbol": "kJ/kg", "Meaning": "Enthalpy",                 "Units": "Refer to Psychrometric Chart"},
]

layout = html.Div(
    style={"width": "100%", "margin": "20px auto", "fontFamily": "Segoe UI, Inter, Arial", "color": BLACK},
    children=[
        # Page header
        html.Div(
            style={"display": "flex", "alignItems": "center", "gap": "20px", "marginBottom": "18px"},
            children=[
                html.Div(style={"width": "12px", "height": "32px", "backgroundColor": BRAND, "borderRadius": "6px"}),
                html.H1("Equations", style={"margin": "0", "fontSize": "28px"}),
            ]
        ),
        html.P("Quick calculators for common HVAC equations.", style={"color": MUTED, "marginTop": 0}),

        # --- all cards wrapped in one flex column with spacing ---
        html.Div(
            style={"display": "flex", "flexDirection": "column", "gap": "30px"},
            children=[

                # Abbreviations (centred table)
                section_card(
                    "Abbreviations",
                    [],
                    controls_row=[],
                    result_id="abbr-none",
                    extra_children=dash_table.DataTable(
                        columns=[{"name": "Symbol", "id": "Symbol"},
                                 {"name": "Meaning", "id": "Meaning"},
                                 {"name": "Units", "id": "Units"}],
                        data=abbr_rows,
                        style_cell={"padding": "8px", "textAlign": "center"},
                        style_header={"backgroundColor": "#f5f5f5", "fontWeight": "bold"},
                        style_table={"margin": "6px auto 0", "width": "80%", "borderRadius": "10px", "overflow": "hidden"},
                    )
                ),

                # Heat Content of Air (Latent + Sensible)
                section_card(
                    "Heat Content of Air",
                    [
                        "Latent (watts) = 2.9 × Q × Δ(g/kg)",
                        "Sensible (watts) = 1.213 × Q × ΔT",
                    ],
                    controls_row=[
                        input_box("air-Q", 100.0, step=1, width="115px"), html.Div("Q (L/s)"),
                        input_box("air-dg", 2.0,   step=0.1, width="115px"), html.Div("Δ(g/kg)"),
                        input_box("air-dT", 10.0,  step=0.5, width="115px"), html.Div("ΔT (°C)"),
                    ],
                    result_id="air-heat-out"
                ),

                # Heat Content of Water
                section_card(
                    "Heat Content of Water",
                    ["Total (watts) = 4.187 × Q × ΔT"],
                    controls_row=[
                        input_box("water-Q", 2.0,  step=0.1, width="120px"), html.Div("Q (L/s)"),
                        input_box("water-dT", 5.0, step=0.5, width="120px"), html.Div("ΔT (°C)"),
                    ],
                    result_id="water-heat-out"
                ),

                # Air Flow
                section_card(
                    "Air Flow",
                    ["Air Flow (Q) = A × v × 1000"],
                    controls_row=[
                        input_box("af-A", 0.1, step=0.01, width="120px"), html.Div("A (m²)"),
                        input_box("af-v", 3.0, step=0.1,  width="120px"), html.Div("v (m/s)"),
                    ],
                    result_id="airflow-out"
                ),

                # Air Change
                section_card(
                    "Air Change",
                    ["Air Change Per Hour = 3.6 × Q / V"],
                    controls_row=[
                        input_box("ach-Q", 200.0, step=1,   width="120px"), html.Div("Q (L/s)"),
                        input_box("ach-V", 250.0, step=1.0, width="120px"), html.Div("V (m³)"),
                    ],
                    result_id="ach-out"
                ),

                # Air/Water Mixing
                section_card(
                    "Air/Water Mixing",
                    [],  # no bullets
                    controls_row=[
                        # Row 1: Equation
                        html.Div(
                            dcc.Markdown(
                                r"$$T_3 = \frac{Q_1 \cdot T_1 + Q_2 \cdot T_2}{Q_3}$$",
                                mathjax=True,
                                style={"textAlign": "center", "width": "100%", "marginBottom": "15px"}
                            ),
                            style={"width": "100%"}
                        ),

                        # Row 2: Inputs
                        html.Div([
                            html.Div([
                                html.Label("Q₁ (L/s)"),
                                input_box("mix-Q1", 100.0, step=1, width="140px"),
                            ], style={"display": "flex", "flexDirection": "column"}),

                            html.Div([
                                html.Label("T₁ (°C)"),
                                input_box("mix-T1", 20.0, step=0.5, width="140px"),
                            ], style={"display": "flex", "flexDirection": "column"}),

                            html.Div([
                                html.Label("Q₂ (L/s)"),
                                input_box("mix-Q2", 200.0, step=1, width="140px"),
                            ], style={"display": "flex", "flexDirection": "column"}),

                            html.Div([
                                html.Label("T₂ (°C)"),
                                input_box("mix-T2", 25.0, step=0.5, width="140px"),
                            ], style={"display": "flex", "flexDirection": "column"}),
                        ], style={"display": "flex", "gap": "24px", "flexWrap": "wrap", "justifyContent": "center"}),
                    ],
                    result_id="mix-T3-out",
                    extra_children=html.Div(
                        children=[
                            html.Img(
                                src="/apps/assets/air-water-mixing.png",
                                alt="Air/Water Mixing diagram",
                                style={
                                    "maxWidth": "500px", "width": "100%",
                                    "marginTop": "20px",
                                    "borderRadius": "8px",
                                    "boxShadow": "0 2px 10px rgba(0,0,0,0.1)"
                                }
                            )
                        ],
                        style={"textAlign": "center"}
                    )
                ),

            ]
        ),

        # Footer
        html.Div("AWP • Mechanical Handbook", style={"textAlign": "center", "color": "#5f6368", "marginTop": "22px"}),
    ]
)

# --------- Callbacks ---------

@callback(Output("air-heat-out", "children"),
          Input("air-Q", "value"), Input("air-dg", "value"), Input("air-dT", "value"))
def calc_air_heat(Q_ls, d_gkg, dT):
    if Q_ls is None or d_gkg is None or dT is None:
        return ""
    latent_W   = 2.9   * Q_ls * d_gkg
    sensible_W = 1.213 * Q_ls * dT
    total_W    = latent_W + sensible_W
    return f"Latent = {latent_W:,.1f} W   •   Sensible = {sensible_W:,.1f} W   •   Total = {total_W:,.1f} W"

@callback(Output("water-heat-out", "children"),
          Input("water-Q", "value"), Input("water-dT", "value"))
def calc_water_heat(Q_ls, dT):
    if Q_ls is None or dT is None:
        return ""
    watts = 4.187 * Q_ls * dT * 1000.0
    return f"Total ≈ {watts:,.0f} W  ({watts/1000:,.2f} kW)"

@callback(Output("airflow-out", "children"),
          Input("af-A", "value"), Input("af-v", "value"))
def calc_airflow(A_m2, v_ms):
    if A_m2 is None or v_ms is None:
        return ""
    Q_ls = A_m2 * v_ms * 1000.0
    return f"Q ≈ {Q_ls:,.1f} L/s"

@callback(Output("ach-out", "children"),
          Input("ach-Q", "value"), Input("ach-V", "value"))
def calc_ach(Q_ls, V_m3):
    if Q_ls is None or V_m3 is None or V_m3 == 0:
        return ""
    ach = 3.6 * Q_ls / V_m3
    return f"Air Changes per Hour ≈ {ach:,.2f} ACH"

@callback(Output("mix-T3-out", "children"),
          Input("mix-Q1", "value"), 
          Input("mix-T1", "value"),
          Input("mix-Q2", "value"), 
          Input("mix-T2", "value"))
def calc_mixed_temp(Q1,T1,Q2,T2):
    if None in (Q1, T1, Q2, T2):
        return ""
    Q3 = Q1+Q2
    if Q3 == 0:
        return "Q₃ = 0 (cannot divide)"
    T3 = (Q1*T1 + Q2*T2)/Q3
    return f"T₃ ≈ {T3:,.2f} °C"