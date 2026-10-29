# apps/pages/duct_calculator.py
import math
import re

from dash import register_page, html, dcc, Input, Output, callback

from apps.shared.ui import BRAND, MUTED, BLACK

register_page(__name__, path="/duct-calculator", name="Duct Calculator")

# =====================================================================
# DATA
# =====================================================================
FLOW_UNITS = {
    "L/s": 1.0,
    "m³/s": 1000.0,
    "m³/h": 1000.0 / 3600.0,
    "CFM": 0.4719474,
}

# Same roughness values as the Ductulator page (metres)
ROUGHNESS = {
    "Galvanised steel — 0.15 mm": 0.00015,
    "Spiral steel — 0.09 mm": 0.00009,
    "Flexible duct (fully extended) — 0.9 mm": 0.0009,
    "Custom…": None,
}

# Flexible duct: assumed wall roughness (fully extended). This is an approximation.
FLEX_EPS = 0.0009  # 0.9 mm: ASHRAE Fundamentals "medium rough" category for fully extended flexible duct

STANDARD_ROUND_MM = [
    100, 125, 150, 175, 200, 225, 250, 300, 350, 400, 450, 500, 550, 600,
    650, 700, 750, 800, 850, 900, 1000, 1100, 1200, 1300, 1400, 1500, 1600,
    1800, 2000,
]

# AWP rule: flexible duct runs are limited to 6 m (longer runs are inefficient and carry significant risk)
FLEX_MAX_LENGTH_M = 6.0

FLEX_SIZES_MM = [100, 150, 200, 250, 300, 350, 400, 450, 500]
FLEX_INTERMEDIATE_MM = [125, 175, 225]

ASPECT_RATIOS = [1.0, 1.5, 2.0, 2.5, 3.0, 3.5, 4.0]

# AWP Ductwork Rules of Thumb (same values as the Ductwork Rules page)
LIMIT_FRICTION_PA_M = 1.2
LIMIT_SUPPLY_MS = 7.0

VELOCITY_GUIDE = [
    ("Supply duct", "≤ 7.0 m/s"),
    ("Return duct", "≤ 6.5 m/s"),
    ("Return (behind R/A grille)", "3.0 m/s"),
    ("Exhaust duct", "6.5 m/s"),
    ("Flexible supply", "3.5 m/s"),
    ("Supply register neck", "2.5 m/s"),
    ("Cooling coil face", "2.25 m/s"),
    ("Heating coil face", "3.5 m/s"),
    ("Air filter face", "1.8 – 2.5 m/s"),
    ("Outside air louvre", "1.8 – 2.0 m/s"),
    ("Exhaust louvre", "2.5 m/s"),
    ("Door grille face", "1.25 m/s"),
]

# =====================================================================
# PHYSICS (no Dash in here, so it can be tested on its own)
# =====================================================================
def air_props(temp_c):
    """Air density (kg/m3) and dynamic viscosity (Pa.s) at sea level."""
    t = temp_c + 273.15
    rho = 1.20 * 293.15 / t                       # 1.20 kg/m3 at 20 C
    mu = 1.716e-5 * (t / 273.15) ** 1.5 * (273.15 + 110.4) / (t + 110.4)  # Sutherland
    return rho, mu


def friction_factor(Re, rel_rough):
    """Darcy friction factor. Laminar below Re 2300, Colebrook-White above."""
    if Re <= 0:
        return 0.0
    if Re < 2300:
        return 64.0 / Re
    f = 0.25 / (math.log10(rel_rough / 3.7 + 5.74 / Re ** 0.9)) ** 2
    for _ in range(60):
        new = (-2.0 * math.log10(rel_rough / 3.7 + 2.51 / (Re * math.sqrt(f)))) ** -2
        if abs(new - f) < 1e-10:
            f = new
            break
        f = new
    return f


def round_drop(Q, D, eps, rho, mu):
    """Straight round duct. Q in m3/s, D in m. Returns (V, Pa/m, Re, f)."""
    A = math.pi * D * D / 4.0
    V = Q / A
    Re = rho * V * D / mu
    f = friction_factor(Re, eps / D)
    dp = f / D * rho * V * V / 2.0
    return V, dp, Re, f


def de_rect(w, h):
    """ASHRAE equal-friction equivalent round diameter of a rectangular duct (m)."""
    return 1.30 * (w * h) ** 0.625 / (w + h) ** 0.25


def oval_area(a, b):
    return math.pi * b * b / 4.0 + b * (a - b)


def oval_perimeter(a, b):
    return math.pi * b + 2.0 * (a - b)


def de_oval(a, b):
    """ASHRAE equal-friction equivalent round diameter of a flat oval duct (m)."""
    return 1.55 * oval_area(a, b) ** 0.625 / oval_perimeter(a, b) ** 0.25


def solve_monotonic(fn, target, lo, hi, iters=100):
    """Find x in [lo, hi] where fn(x) == target, for a steadily rising or falling fn."""
    flo = fn(lo)
    fhi = fn(hi)
    if (flo - target) * (fhi - target) > 0:
        return None
    for _ in range(iters):
        mid = 0.5 * (lo + hi)
        fm = fn(mid)
        if (fm - target) * (flo - target) <= 0:
            hi = mid
        else:
            lo, flo = mid, fm
    return 0.5 * (lo + hi)


def ceil_to(value_m, inc_mm):
    """Round a size UP to the next construction increment. Returns metres."""
    mm = value_m * 1000.0
    steps = max(1, math.ceil(mm / inc_mm - 1e-9))
    return steps * inc_mm / 1000.0


def rect_result(Q, w, h, eps, rho, mu):
    V = Q / (w * h)
    De = de_rect(w, h)
    dp = round_drop(Q, De, eps, rho, mu)[1]
    return V, dp, De


def size_rect(Q, method, target, ratio, inc_mm, eps, rho, mu):
    """Recommend a rectangular duct. method = 'friction' (Pa/m) or 'velocity' (m/s)."""
    if method == "friction":
        D_t = solve_monotonic(lambda D: round_drop(Q, D, eps, rho, mu)[1], target, 0.03, 6.0)
        if D_t is None:
            return None
        h_ideal = solve_monotonic(lambda h: de_rect(ratio * h, h), D_t, 0.005, 10.0)
        if h_ideal is None:
            return None
    else:
        area = Q / target
        h_ideal = math.sqrt(area / ratio)
    w_ideal = ratio * h_ideal
    w = ceil_to(w_ideal, inc_mm)
    h = ceil_to(h_ideal, inc_mm)
    V, dp, De = rect_result(Q, w, h, eps, rho, mu)
    return {"w": w, "h": h, "V": V, "dp": dp, "De": De, "ratio": ratio}


def pick_standard_round(Q, method, target, eps, rho, mu):
    """Smallest standard round duct that meets the target."""
    for d in STANDARD_ROUND_MM:
        V, dp, _, _ = round_drop(Q, d / 1000.0, eps, rho, mu)
        ok = (dp <= target) if method == "friction" else (V <= target)
        if ok:
            return {"d": d, "V": V, "dp": dp, "meets": True}
    d = STANDARD_ROUND_MM[-1]
    V, dp, _, _ = round_drop(Q, d / 1000.0, eps, rho, mu)
    return {"d": d, "V": V, "dp": dp, "meets": False}


def convert_shapes(Q, method, shape, dims_mm, out_w_mm, out_a_mm, eps, rho, mu):
    """Convert a duct between rectangular, round and flat oval.
    Returns a dict, or a string describing the problem."""
    if shape == "rect":
        w, h = dims_mm[0] / 1000.0, dims_mm[1] / 1000.0
        A, De = w * h, de_rect(w, h)
    elif shape == "round":
        D = dims_mm[0] / 1000.0
        A, De = math.pi * D * D / 4.0, D
    else:
        a, b = dims_mm[0] / 1000.0, dims_mm[1] / 1000.0
        if b > a:
            return "For a flat oval, the minor axis must not be larger than the major axis."
        A, De = oval_area(a, b), de_oval(a, b)

    src_dp = round_drop(Q, De, eps, rho, mu)[1]
    ow, oa = out_w_mm / 1000.0, out_a_mm / 1000.0

    if method == "area":
        rect_h = A / ow
        round_d = math.sqrt(4.0 * A / math.pi)
        k = 1.0 - math.pi / 4.0
        disc = oa * oa - 4.0 * k * A
        oval_b = None if disc < 0 else (oa - math.sqrt(disc)) / (2.0 * k)
    else:
        rect_h = solve_monotonic(lambda x: de_rect(ow, x), De, 0.005, 20.0)
        round_d = De
        oval_b = solve_monotonic(lambda x: de_oval(oa, x), De, 0.005, oa)

    out = {"src_dp": src_dp, "src_De": De, "rect": None, "round": None, "oval": None}

    if rect_h:
        V, dp, _ = rect_result(Q, ow, rect_h, eps, rho, mu)
        out["rect"] = {"w": ow, "h": rect_h, "V": V, "dp": dp}
    if round_d:
        V, dp, _, _ = round_drop(Q, round_d, eps, rho, mu)
        out["round"] = {"d": round_d, "V": V, "dp": dp}
    if oval_b and oval_b > 0:
        Ao = oval_area(oa, oval_b)
        V = Q / Ao
        dp = round_drop(Q, de_oval(oa, oval_b), eps, rho, mu)[1]
        out["oval"] = {"a": oa, "b": oval_b, "V": V, "dp": dp}
    return out


def flexible_table(Q, sizes_mm, factor, rho, mu):
    rows = []
    for d in sizes_mm:
        V, dp, _, _ = round_drop(Q, d / 1000.0, FLEX_EPS, rho, mu)
        rows.append({"d": d, "V": V, "dp": dp * factor})
    return rows


_FLOW_OK = re.compile(r"\s*[+-]?\s*(\d+\.?\d*|\.\d+)(\s*[+-]\s*(\d+\.?\d*|\.\d+))*\s*")
_FLOW_PART = re.compile(r"([+-]?)\s*(\d+\.?\d*|\.\d+)")


def parse_flow(text, unit):
    """Turn '300+450' (or a plain number) into litres/second. None if not valid."""
    if text is None:
        return None
    s = str(text).strip()
    if not _FLOW_OK.fullmatch(s):
        return None
    total = 0.0
    for sign, num in _FLOW_PART.findall(s):
        total += -float(num) if sign == "-" else float(num)
    q_ls = total * FLOW_UNITS.get(unit, 1.0)
    return q_ls if q_ls > 0 else None


def get_eps(material, custom_mm):
    eps = ROUGHNESS.get(material, 0.00015)
    if eps is None:
        try:
            eps = max(float(custom_mm), 0.0) / 1000.0
        except Exception:
            eps = 0.00015
    return eps


def get_air(temp_c):
    try:
        t = float(temp_c)
    except Exception:
        t = 20.0
    return air_props(min(max(t, -40.0), 120.0))


def pos_number(value):
    try:
        v = float(value)
    except Exception:
        return None
    return v if v > 0 else None


# =====================================================================
# UI HELPERS
# =====================================================================
FONT = "Segoe UI, Inter, Arial"
LABEL = {"fontWeight": 600, "fontSize": "14px", "marginBottom": "4px", "display": "block"}
HINT = {"fontSize": "12px", "color": MUTED, "marginTop": "3px"}
CARD = {
    "background": "#fff",
    "border": "1px solid #e5e5e5",
    "borderLeft": f"6px solid {BRAND}",
    "borderRadius": "12px",
    "padding": "16px 18px",
    "boxShadow": "0 4px 14px rgba(0,0,0,0.04)",
}
INPUT = {"width": "100%", "padding": "9px 10px", "borderRadius": "8px",
         "border": "1px solid #d0d0d0", "boxSizing": "border-box"}
SHOW = {"display": "block"}
HIDE = {"display": "none"}


def fmt(x, d=2):
    return f"{x:,.{d}f}"


def mm(x_m):
    return f"{x_m * 1000:,.0f}"


def field(label, control, hint=None, **kw):
    kids = [html.Label(label, style=LABEL), control]
    if hint:
        kids.append(html.Div(hint, style=HINT))
    return html.Div(kids, style={"marginBottom": "14px"}, **kw)


def flow_input(prefix, default="1000"):
    return field(
        "Airflow",
        html.Div(
            [
                dcc.Input(id=f"{prefix}-flow", type="text", value=default, debounce=True,
                          style={**INPUT, "flex": "1"}),
                html.Div(
                    dcc.Dropdown(id=f"{prefix}-unit",
                                 options=[{"label": u, "value": u} for u in FLOW_UNITS],
                                 value="L/s", clearable=False),
                    style={"width": "110px"},
                ),
            ],
            style={"display": "flex", "gap": "8px", "alignItems": "center"},
        ),
        "Type a number or a simple sum such as 300+450, then press Enter.",
    )


def num_input(_id, value, step=1, minimum=None):
    return dcc.Input(id=_id, type="number", value=value, step=step, min=minimum, style=INPUT)


def tile(label, value, unit="", sub=None, big=False):
    return html.Div(
        [
            html.Div(label, style={"fontSize": "11px", "letterSpacing": "0.06em",
                                   "textTransform": "uppercase", "color": MUTED}),
            html.Div(
                [html.Span(value, style={"fontSize": "30px" if big else "24px", "fontWeight": 700}),
                 html.Span(f" {unit}", style={"color": MUTED, "marginLeft": "2px"})],
                style={"marginTop": "4px"},
            ),
            html.Div(sub, style=HINT) if sub else None,
        ],
        style={"border": "1px solid #e8e8e8", "borderRadius": "10px", "padding": "12px 14px",
               "background": "#fafafa"},
    )


def tile_grid(children, cols=3):
    return html.Div(children, style={"display": "grid", "gap": "10px",
                                     "gridTemplateColumns": f"repeat({cols}, minmax(0, 1fr))",
                                     "marginBottom": "12px"})


def banner(ok, title, lines):
    colour = ("#e8f5e9", "#1b5e20", "#a5d6a7") if ok else ("#fff8e1", "#8a5a00", "#ffe082")
    return html.Div(
        [html.Div(("✔ " if ok else "⚠ ") + title, style={"fontWeight": 700}),
         *[html.Div(x, style={"fontSize": "13px", "marginTop": "2px"}) for x in lines]],
        style={"background": colour[0], "color": colour[1], "border": f"1px solid {colour[2]}",
               "borderRadius": "10px", "padding": "10px 14px", "marginBottom": "12px"},
    )


def error_box(msg):
    return html.Div(msg, style={"background": "#fdecea", "color": "#8a1c13", "border": "1px solid #f5c2bd",
                                "borderRadius": "10px", "padding": "12px 14px"})


def checks(V, dp, label="Preliminary checks"):
    """Compare against the AWP rules of thumb (max supply velocity and friction rate)."""
    issues = []
    if dp > LIMIT_FRICTION_PA_M:
        issues.append(f"Friction rate {dp:.2f} Pa/m is above the AWP rule of thumb of {LIMIT_FRICTION_PA_M} Pa/m.")
    if V > LIMIT_SUPPLY_MS:
        issues.append(f"Velocity {V:.2f} m/s is above the AWP supply limit of {LIMIT_SUPPLY_MS} m/s.")
    if issues:
        return banner(False, label + " — check these", issues)
    return banner(True, label + " passed",
                  [f"Within AWP rules of thumb (≤ {LIMIT_FRICTION_PA_M} Pa/m and ≤ {LIMIT_SUPPLY_MS} m/s supply)."])


def th(text, align="left"):
    return html.Th(text, style={"textAlign": align, "padding": "8px 10px", "fontSize": "12px",
                                "color": MUTED, "borderBottom": "1px solid #ddd"})


def td(text, align="left", bold=False):
    return html.Td(text, style={"textAlign": align, "padding": "8px 10px", "fontSize": "14px",
                                "fontWeight": 700 if bold else 400})


# =====================================================================
# LAYOUT
# =====================================================================
TAB_STYLE = {"padding": "10px 14px", "fontFamily": FONT}
TAB_SELECTED = {"padding": "10px 14px", "fontFamily": FONT, "fontWeight": 700,
                "borderTop": f"3px solid {BRAND}"}

settings_card = html.Div(
    [
        html.H3("Duct and air settings", style={"margin": "0 0 10px 0", "fontSize": "18px"}),
        html.Div(
            [
                field("Duct material",
                      dcc.Dropdown(id="dc-material",
                                   options=[{"label": k, "value": k} for k in ROUGHNESS],
                                   value="Galvanised steel — 0.15 mm", clearable=False)),
                html.Div(field("Custom roughness ε (mm)", num_input("dc-rough-custom", 0.15, step=0.01, minimum=0)),
                         id="dc-rough-custom-row", style=HIDE),
                field("Air temperature (°C)", num_input("dc-temp", 20, step=1),
                      "Sea-level air. Density is 1.20 kg/m³ at 20 °C."),
            ],
            style={"display": "grid", "gridTemplateColumns": "repeat(auto-fit, minmax(220px, 1fr))",
                   "gap": "14px"},
        ),
        html.Div("Material applies to the first three tabs. The Flexible duct sizer always uses flexible duct. Air temperature applies to every tab.", style=HINT),
    ],
    style={**CARD, "marginBottom": "16px"},
)

size_tab = html.Div(
    [
        html.Div(
            [
                html.Div(
                    [
                        html.H3("Design inputs", style={"marginTop": 0}),
                        flow_input("dc-s"),
                        field("Sizing method",
                              dcc.RadioItems(id="dc-s-method",
                                             options=[{"label": " Equal friction (target Pa/m)", "value": "friction"},
                                                      {"label": " Constant velocity (target m/s)", "value": "velocity"}],
                                             value="friction", labelStyle={"display": "block", "marginBottom": "4px"})),
                        html.Div(
                            field("Friction rate target (Pa/m)",
                                  dcc.Slider(id="dc-s-friction", min=0.1, max=2.5, step=0.05, value=0.8,
                                             marks={0.1: "0.1", 1.2: "1.2", 2.5: "2.5"},
                                             tooltip={"placement": "bottom"}),
                                  "AWP rule of thumb: 0.8 – 1.2 Pa/m."),
                            id="dc-s-friction-wrap", style=SHOW),
                        html.Div(
                            field("Velocity target (m/s)",
                                  dcc.Slider(id="dc-s-velocity", min=1, max=12, step=0.5, value=5,
                                             marks={1: "1", 7: "7", 12: "12"},
                                             tooltip={"placement": "bottom"}),
                                  "AWP rule of thumb: supply up to 7.0 m/s."),
                            id="dc-s-velocity-wrap", style=HIDE),
                        field("Preferred aspect ratio (W : H)",
                              dcc.Slider(id="dc-s-ratio", min=1, max=4, step=0.5, value=2,
                                         marks={1: "1:1", 2: "2:1", 3: "3:1", 4: "4:1"},
                                         tooltip={"placement": "bottom"})),
                        field("Construction increment",
                              dcc.Dropdown(id="dc-s-inc",
                                           options=[{"label": f"{x} mm", "value": x} for x in (25, 50, 100)],
                                           value=50, clearable=False),
                              "Sizes are rounded UP to the next increment."),
                    ],
                    style=CARD,
                ),
                html.Div([html.Div(id="dc-s-result")], style={"minWidth": 0}),
            ],
            style={"display": "grid", "gridTemplateColumns": "minmax(280px, 1fr) minmax(0, 1.6fr)", "gap": "16px",
                   "alignItems": "start"},
        ),
        html.Div(id="dc-s-alt", style={"marginTop": "16px"}),
    ]
)

check_tab = html.Div(
    html.Div(
        [
            html.Div(
                [
                    html.H3("Design inputs", style={"marginTop": 0}),
                    flow_input("dc-c"),
                    field("Duct shape",
                          dcc.RadioItems(id="dc-c-shape",
                                         options=[{"label": " Round", "value": "round"},
                                                  {"label": " Rectangular", "value": "rect"}],
                                         value="round", inline=True, labelStyle={"marginRight": "14px"})),
                    html.Div(field("Internal diameter (mm)", num_input("dc-c-diam", 500, step=5, minimum=0)),
                             id="dc-c-round-row", style=SHOW),
                    html.Div([field("Width (mm)", num_input("dc-c-w", 600, step=10, minimum=0)),
                              field("Height (mm)", num_input("dc-c-h", 300, step=10, minimum=0))],
                             id="dc-c-rect-row", style=HIDE),
                    field("Straight length (m)", num_input("dc-c-length", 10, step=0.5, minimum=0)),
                    field("Fitting loss coefficient K (optional)", num_input("dc-c-k", 0, step=0.01, minimum=0),
                          "Fitting loss = K × velocity pressure. Use K values from the Duct Fitting Coefficients page."),
                ],
                style=CARD,
            ),
            html.Div(id="dc-c-result"),
        ],
        style={"display": "grid", "gridTemplateColumns": "minmax(280px, 1fr) minmax(0, 1.6fr)", "gap": "16px",
               "alignItems": "start"},
    )
)

convert_tab = html.Div(
    html.Div(
        [
            html.Div(
                [
                    html.H3("Source duct", style={"marginTop": 0}),
                    flow_input("dc-v"),
                    field("Conversion method",
                          dcc.RadioItems(id="dc-v-method",
                                         options=[{"label": " Equal friction (same Pa/m)", "value": "friction"},
                                                  {"label": " Equal area (same cross-section)", "value": "area"}],
                                         value="friction", labelStyle={"display": "block", "marginBottom": "4px"})),
                    field("Source shape",
                          dcc.RadioItems(id="dc-v-shape",
                                         options=[{"label": " Rectangular", "value": "rect"},
                                                  {"label": " Round", "value": "round"},
                                                  {"label": " Flat oval", "value": "oval"}],
                                         value="rect", inline=True, labelStyle={"marginRight": "14px"})),
                    html.Div([field("Width (mm)", num_input("dc-v-w", 600, step=10, minimum=0)),
                              field("Height (mm)", num_input("dc-v-h", 300, step=10, minimum=0))],
                             id="dc-v-rect-row", style=SHOW),
                    html.Div([field("Diameter (mm)", num_input("dc-v-d", 500, step=10, minimum=0))],
                             id="dc-v-round-row", style=HIDE),
                    html.Div([field("Major axis (mm)", num_input("dc-v-a", 600, step=10, minimum=0)),
                              field("Minor axis (mm)", num_input("dc-v-b", 300, step=10, minimum=0))],
                             id="dc-v-oval-row", style=HIDE),
                    html.H4("Output sizes to hold fixed", style={"marginBottom": "6px"}),
                    html.Div(field("Rectangular output width (mm)", num_input("dc-v-outw", 600, step=10, minimum=0)),
                             id="dc-v-outw-row", style=HIDE),
                    html.Div(field("Flat oval output major axis (mm)", num_input("dc-v-outa", 600, step=10, minimum=0)),
                             id="dc-v-outa-row", style=SHOW),
                ],
                style=CARD,
            ),
            html.Div(id="dc-v-result"),
        ],
        style={"display": "grid", "gridTemplateColumns": "minmax(280px, 1fr) minmax(0, 1.6fr)", "gap": "16px",
               "alignItems": "start"},
    )
)

flex_tab = html.Div(
    html.Div(
        [
            html.Div(
                [
                    html.H3("Design inputs", style={"marginTop": 0}),
                    flow_input("dc-f", default="300"),
                    field("Target friction rate (Pa/m)", num_input("dc-f-friction", 1.0, step=0.1, minimum=0)),
                    field("Maximum velocity (m/s)", num_input("dc-f-vmax", 3.5, step=0.1, minimum=0),
                          "AWP rule of thumb for flexible supply duct: 3.5 m/s."),
                    field("Straight length (m)", num_input("dc-f-length", 5, step=0.5, minimum=0),
                          f"AWP maximum is {FLEX_MAX_LENGTH_M:g} m. Longer flexible runs are inefficient and carry significant risk, so use rigid duct instead."),
                    field("Installation correction factor", num_input("dc-f-factor", 1.0, step=0.05, minimum=0),
                          "1.0 = fully extended. For compressed or sagging duct, enter the manufacturer's factor."),
                    dcc.Checklist(id="dc-f-inter",
                                  options=[{"label": " Include intermediate 125, 175 and 225 mm sizes", "value": "yes"}],
                                  value=[]),
                ],
                style=CARD,
            ),
            html.Div(id="dc-f-result"),
        ],
        style={"display": "grid", "gridTemplateColumns": "minmax(280px, 1fr) minmax(0, 1.6fr)", "gap": "16px",
               "alignItems": "start"},
    )
)

velocity_guide = html.Div(
    [
        html.Div("ENGINEERING REFERENCE", style={"fontSize": "11px", "letterSpacing": "0.08em", "color": MUTED}),
        html.H3("Typical velocity guide (AWP rules of thumb)", style={"margin": "2px 0 10px 0"}),
        html.Div(
            [html.Div([html.Div(n, style={"fontSize": "12px", "color": MUTED}),
                       html.Div(v, style={"fontWeight": 700})],
                      style={"border": "1px solid #e8e8e8", "borderRadius": "8px", "padding": "8px 12px",
                             "background": "#fafafa"})
             for n, v in VELOCITY_GUIDE],
            style={"display": "grid", "gap": "8px", "gridTemplateColumns": "repeat(auto-fill, minmax(190px, 1fr))"},
        ),
        html.Div("Always confirm acoustic, pressure and equipment requirements for the project.", style=HINT),
    ],
    style={**CARD, "marginTop": "18px"},
)

method_card = html.Div(
    [
        html.Div("HELP AND METHOD", style={"fontSize": "11px", "letterSpacing": "0.08em", "color": MUTED}),
        html.H3("How these results are calculated", style={"margin": "2px 0 8px 0"}),
        html.Ul(
            [
                html.Li("Straight-duct friction uses Darcy–Weisbach with the Colebrook–White friction factor."),
                html.Li("Rectangular and flat oval ducts are converted to an equal-friction round duct "
                        "(ASHRAE equivalent diameter) at the same airflow."),
                html.Li("Equal friction sizes the duct to a target Pa/m. Constant velocity sizes it to a target m/s."),
                html.Li("Sizes are rounded up to the construction increment, so results are slightly conservative."),
                html.Li("Excluded: fittings, transitions, leakage, heat gain, noise and equipment pressure drops."),
                html.Li("Results are for preliminary sizing. Different equivalent-diameter methods can differ by a "
                        "few percent for rectangular ducts."),
            ],
            style={"color": "#333", "fontSize": "14px", "lineHeight": "1.6", "marginBottom": 0},
        ),
    ],
    style={**CARD, "marginTop": "16px"},
)

layout = html.Div(
    style={"width": "100%", "padding": "16px", "fontFamily": FONT, "color": BLACK},
    children=[
        html.Div(
            style={"display": "flex", "alignItems": "center", "gap": "14px", "marginBottom": "6px"},
            children=[
                html.Div(style={"width": "12px", "height": "28px", "backgroundColor": BRAND, "borderRadius": "6px"}),
                html.H2("Duct Calculator", style={"margin": 0}),
            ],
        ),
        html.P("Size, check and convert rigid and flexible ductwork (SI units).",
               style={"color": MUTED, "marginTop": 0, "marginBottom": "14px"}),
        settings_card,
        dcc.Tabs(
            id="dc-tabs", value="size",
            children=[
                dcc.Tab(label="Size a duct", value="size", children=[html.Div(size_tab, style={"paddingTop": "16px"})],
                        style=TAB_STYLE, selected_style=TAB_SELECTED),
                dcc.Tab(label="Check a duct", value="check", children=[html.Div(check_tab, style={"paddingTop": "16px"})],
                        style=TAB_STYLE, selected_style=TAB_SELECTED),
                dcc.Tab(label="Duct shape converter", value="convert",
                        children=[html.Div(convert_tab, style={"paddingTop": "16px"})],
                        style=TAB_STYLE, selected_style=TAB_SELECTED),
                dcc.Tab(label="Flexible duct sizer", value="flex", children=[html.Div(flex_tab, style={"paddingTop": "16px"})],
                        style=TAB_STYLE, selected_style=TAB_SELECTED),
            ],
        ),
        velocity_guide,
        method_card,
    ],
)

# =====================================================================
# CALLBACKS
# =====================================================================
@callback(Output("dc-rough-custom-row", "style"), Input("dc-material", "value"))
def toggle_custom_roughness(material):
    return SHOW if ROUGHNESS.get(material, 0.0) is None else HIDE


@callback(
    Output("dc-s-friction-wrap", "style"),
    Output("dc-s-velocity-wrap", "style"),
    Input("dc-s-method", "value"),
)
def toggle_size_method(method):
    return (SHOW, HIDE) if method == "friction" else (HIDE, SHOW)


@callback(
    Output("dc-v-rect-row", "style"),
    Output("dc-v-round-row", "style"),
    Output("dc-v-oval-row", "style"),
    Output("dc-v-outw-row", "style"),
    Output("dc-v-outa-row", "style"),
    Input("dc-v-shape", "value"),
)
def toggle_source_shape(shape):
    return (
        SHOW if shape == "rect" else HIDE,
        SHOW if shape == "round" else HIDE,
        SHOW if shape == "oval" else HIDE,
        HIDE if shape == "rect" else SHOW,   # rectangular output width only needed when source is not rectangular
        HIDE if shape == "oval" else SHOW,   # oval major axis only needed when source is not oval
    )


# ---------------- Tab 1: Size a duct ----------------
@callback(
    Output("dc-s-result", "children"),
    Output("dc-s-alt", "children"),
    Input("dc-s-flow", "value"),
    Input("dc-s-unit", "value"),
    Input("dc-s-method", "value"),
    Input("dc-s-friction", "value"),
    Input("dc-s-velocity", "value"),
    Input("dc-s-ratio", "value"),
    Input("dc-s-inc", "value"),
    Input("dc-temp", "value"),
    Input("dc-material", "value"),
    Input("dc-rough-custom", "value"),
)
def update_size(flow_text, unit, method, friction_t, velocity_t, ratio, inc, temp, material, rough_custom):
    q_ls = parse_flow(flow_text, unit)
    if q_ls is None:
        return error_box("Enter a valid airflow greater than zero, e.g. 1000 or 300+450."), ""

    Q = q_ls / 1000.0
    rho, mu = get_air(temp)
    eps = get_eps(material, rough_custom)
    target = friction_t if method == "friction" else velocity_t
    ratio = ratio or 2.0
    inc = inc or 50

    rec = size_rect(Q, method, target, ratio, inc, eps, rho, mu)
    if rec is None:
        return error_box("This airflow and target are outside the range the calculator can solve. "
                         "Try a different target."), ""

    std = pick_standard_round(Q, method, target, eps, rho, mu)
    basis = (f"{friction_t:.2f} Pa/m target" if method == "friction" else f"{velocity_t:.1f} m/s target")

    result = html.Div(
        [
            html.Div(
                [
                    html.H3("Recommended duct size", style={"margin": 0}),
                    html.Div(f"Based on {q_ls:,.0f} L/s · {basis} · {ratio:g}:1 aspect ratio", style=HINT),
                    html.Div(
                        [
                            html.Div("RECTANGULAR RIGID DUCT", style={"fontSize": "11px", "letterSpacing": "0.08em",
                                                                      "color": MUTED}),
                            html.Div(f"{mm(rec['w'])} × {mm(rec['h'])} mm",
                                     style={"fontSize": "40px", "fontWeight": 800, "margin": "4px 0"}),
                            html.Div("width × height (internal dimensions)", style=HINT),
                        ],
                        style={"textAlign": "center", "padding": "18px", "background": "#f2f6f2",
                               "borderRadius": "10px", "margin": "12px 0"},
                    ),
                    tile_grid([
                        tile("Actual velocity", fmt(rec["V"]), "m/s"),
                        tile("Pressure loss rate", fmt(rec["dp"], 3), "Pa/m"),
                        tile("Equivalent round Ø", mm(rec["De"]), "mm"),
                    ]),
                    tile_grid([
                        tile("Smallest standard round that meets the target", f"Ø {std['d']}", "mm",
                             sub=f"{std['V']:.2f} m/s · {std['dp']:.3f} Pa/m"
                                 + ("" if std["meets"] else " · largest size listed, target not met")),
                    ], cols=1),
                    checks(rec["V"], rec["dp"]),
                ],
                style=CARD,
            )
        ]
    )

    rows = []
    for r in ASPECT_RATIOS:
        alt = size_rect(Q, method, target, r, inc, eps, rho, mu)
        if alt is None:
            continue
        sel = abs(r - ratio) < 0.01
        rows.append(html.Tr(
            [td(f"{r:g} : 1", bold=sel), td(f"{mm(alt['w'])} × {mm(alt['h'])} mm", bold=sel),
             td(f"{alt['V']:.2f} m/s", "right"), td(f"{alt['dp']:.3f} Pa/m", "right"),
             td(f"Ø {mm(alt['De'])} mm", "right")],
            style={"background": "#eef5ee" if sel else "transparent"},
        ))
    alt_table = html.Div(
        [
            html.H3("Alternative sizes", style={"margin": "0 0 2px 0"}),
            html.Div("Same airflow and target at other aspect ratios.", style=HINT),
            html.Div(
                html.Table(
                    [html.Thead(html.Tr([th("RATIO"), th("DUCT SIZE"), th("VELOCITY", "right"),
                                         th("FRICTION", "right"), th("EQUIVALENT Ø", "right")])),
                     html.Tbody(rows)],
                    style={"width": "100%", "borderCollapse": "collapse"},
                ),
                style={"overflowX": "auto"},
            ),
        ],
        style=CARD,
    )
    return result, alt_table


# ---------------- Tab 2: Check a duct ----------------
@callback(
    Output("dc-c-round-row", "style"),
    Output("dc-c-rect-row", "style"),
    Input("dc-c-shape", "value"),
)
def toggle_check_shape(shape):
    return (SHOW, HIDE) if shape == "round" else (HIDE, SHOW)


@callback(
    Output("dc-c-result", "children"),
    Input("dc-c-flow", "value"),
    Input("dc-c-unit", "value"),
    Input("dc-c-shape", "value"),
    Input("dc-c-diam", "value"),
    Input("dc-c-w", "value"),
    Input("dc-c-h", "value"),
    Input("dc-c-length", "value"),
    Input("dc-c-k", "value"),
    Input("dc-temp", "value"),
    Input("dc-material", "value"),
    Input("dc-rough-custom", "value"),
)
def update_check(flow_text, unit, shape, diam_mm, w_mm, h_mm, length, k, temp, material, rough_custom):
    q_ls = parse_flow(flow_text, unit)
    if q_ls is None:
        return error_box("Enter a valid airflow greater than zero, e.g. 1000 or 300+450.")

    rho, mu = get_air(temp)
    eps = get_eps(material, rough_custom)
    Q = q_ls / 1000.0

    if shape == "round":
        d = pos_number(diam_mm)
        if d is None:
            return error_box("Enter an internal diameter greater than zero.")
        D = d / 1000.0
        area = math.pi * D * D / 4.0
        size_text, tag = f"Ø {d:,.0f} mm", "ROUND DUCT"
        V = Q / area
        De = D
    else:
        w, h = pos_number(w_mm), pos_number(h_mm)
        if w is None or h is None:
            return error_box("Enter a width and height greater than zero.")
        area = (w / 1000.0) * (h / 1000.0)
        size_text, tag = f"{w:,.0f} × {h:,.0f} mm", "RECTANGULAR DUCT"
        V = Q / area
        De = de_rect(w / 1000.0, h / 1000.0)

    _, dp, Re, f = round_drop(Q, De, eps, rho, mu)
    vp = 0.5 * rho * V * V
    try:
        length_m = max(float(length), 0.0)
    except Exception:
        length_m = 0.0
    try:
        k_val = max(float(k), 0.0)
    except Exception:
        k_val = 0.0

    tiles_extra = [
        tile(f"Straight loss over {length_m:g} m", fmt(dp * length_m, 1), "Pa"),
    ]
    if k_val > 0:
        tiles_extra.append(tile(f"Fitting loss (K = {k_val:g})", fmt(k_val * vp, 1), "Pa",
                                sub=f"K × velocity pressure = {k_val:g} × {vp:.2f} Pa"))

    return html.Div(
        [
            html.H3("Entered duct", style={"margin": 0}),
            html.Div(f"Checking {q_ls:,.0f} L/s through {size_text}", style=HINT),
            html.Div(
                [html.Div(tag, style={"fontSize": "11px", "letterSpacing": "0.08em", "color": MUTED}),
                 html.Div(size_text, style={"fontSize": "40px", "fontWeight": 800, "margin": "4px 0"})],
                style={"textAlign": "center", "padding": "18px", "background": "#f2f6f2",
                       "borderRadius": "10px", "margin": "12px 0"},
            ),
            tile_grid([
                tile("Actual velocity", fmt(V), "m/s"),
                tile("Pressure loss rate", fmt(dp, 3), "Pa/m"),
                tile("Internal flow area", fmt(area, 3), "m²"),
            ]),
            tile_grid([
                tile("Velocity pressure", fmt(vp), "Pa"),
                tile("Equivalent round Ø", mm(De), "mm") if shape != "round" else tile("Reynolds number", f"{Re:,.0f}"),
                tile("Friction factor", fmt(f, 4)),
            ]),
            tile_grid(tiles_extra, cols=len(tiles_extra)),
            checks(V, dp),
            html.Div("Total loss = straight loss + fitting loss. Add equipment pressure drops separately.", style=HINT),
        ],
        style=CARD,
    )


# ---------------- Tab 3: Duct shape converter ----------------
@callback(
    Output("dc-v-result", "children"),
    Input("dc-v-flow", "value"),
    Input("dc-v-unit", "value"),
    Input("dc-v-method", "value"),
    Input("dc-v-shape", "value"),
    Input("dc-v-w", "value"),
    Input("dc-v-h", "value"),
    Input("dc-v-d", "value"),
    Input("dc-v-a", "value"),
    Input("dc-v-b", "value"),
    Input("dc-v-outw", "value"),
    Input("dc-v-outa", "value"),
    Input("dc-temp", "value"),
    Input("dc-material", "value"),
    Input("dc-rough-custom", "value"),
)
def update_convert(flow_text, unit, method, shape, w, h, d, a, b, out_w, out_a, temp, material, rough_custom):
    q_ls = parse_flow(flow_text, unit)
    if q_ls is None:
        return error_box("Enter a valid airflow greater than zero, e.g. 1000 or 300+450.")

    if shape == "rect":
        dims = [pos_number(w), pos_number(h)]
    elif shape == "round":
        dims = [pos_number(d)]
    else:
        dims = [pos_number(a), pos_number(b)]
    if any(x is None for x in dims):
        return error_box("Enter all source dimensions as numbers greater than zero.")

    ow, oa = pos_number(out_w), pos_number(out_a)
    if ow is None or oa is None:
        return error_box("Enter the output width and output major axis as numbers greater than zero.")

    rho, mu = get_air(temp)
    eps = get_eps(material, rough_custom)
    res = convert_shapes(q_ls / 1000.0, method, shape, dims, ow, oa, eps, rho, mu)
    if isinstance(res, str):
        return error_box(res)

    def shape_card(title, size_text, data, missing_msg):
        if data is None:
            return html.Div([html.Div(title, style={"fontSize": "11px", "letterSpacing": "0.08em", "color": MUTED}),
                             html.Div(missing_msg, style={"color": "#8a1c13", "marginTop": "6px"})],
                            style={"border": "1px solid #e8e8e8", "borderRadius": "10px", "padding": "12px 14px"})
        return html.Div(
            [html.Div(title, style={"fontSize": "11px", "letterSpacing": "0.08em", "color": MUTED}),
             html.Div(size_text, style={"fontSize": "28px", "fontWeight": 800, "margin": "4px 0"}),
             html.Div(f"{data['V']:.2f} m/s · {data['dp']:.3f} Pa/m", style=HINT)],
            style={"border": "1px solid #e8e8e8", "borderRadius": "10px", "padding": "12px 14px",
                   "background": "#fafafa"},
        )

    rect, rnd, oval = res["rect"], res["round"], res["oval"]
    method_text = "Equal friction" if method == "friction" else "Equal area"
    return html.Div(
        [
            html.H3("Converted sizes", style={"margin": 0}),
            html.Div(f"{method_text} · {q_ls:,.0f} L/s · source friction {res['src_dp']:.3f} Pa/m", style=HINT),
            html.Div(
                [c for c in (
                    shape_card("EQUIVALENT RECTANGULAR",
                               f"{mm(rect['w'])} × {mm(rect['h'])} mm" if rect else "",
                               rect, "No valid height for that width.") if shape != "rect" else None,
                    shape_card("EQUIVALENT ROUND",
                               f"Ø {mm(rnd['d'])} mm" if rnd else "",
                               rnd, "Could not be calculated.") if shape != "round" else None,
                    shape_card("EQUIVALENT FLAT OVAL",
                               f"{mm(oval['a'])} × {mm(oval['b'])} mm" if oval else "",
                               oval, "The major axis is too small for this size. Increase it.") if shape != "oval" else None,
                ) if c is not None],
                style={"display": "grid", "gap": "10px", "marginTop": "12px"},
            ),
            html.Div("Straight-duct friction only. Check velocity, noise and fitting losses separately.",
                     style={**HINT, "marginTop": "10px"}),
        ],
        style=CARD,
    )


# ---------------- Tab 4: Flexible duct sizer ----------------
@callback(
    Output("dc-f-result", "children"),
    Input("dc-f-flow", "value"),
    Input("dc-f-unit", "value"),
    Input("dc-f-friction", "value"),
    Input("dc-f-vmax", "value"),
    Input("dc-f-length", "value"),
    Input("dc-f-factor", "value"),
    Input("dc-f-inter", "value"),
    Input("dc-temp", "value"),
)
def update_flexible(flow_text, unit, friction_t, vmax, length, factor, inter, temp):
    q_ls = parse_flow(flow_text, unit)
    if q_ls is None:
        return error_box("Enter a valid airflow greater than zero, e.g. 300 or 100+200.")
    ft, vm, fac = pos_number(friction_t), pos_number(vmax), pos_number(factor)
    if ft is None or vm is None or fac is None:
        return error_box("Enter the target friction, maximum velocity and correction factor as numbers above zero.")
    try:
        length_m = max(float(length), 0.0)
    except Exception:
        length_m = 0.0
    too_long = length_m > FLEX_MAX_LENGTH_M

    rho, mu = get_air(temp)
    sizes = sorted(FLEX_SIZES_MM + (FLEX_INTERMEDIATE_MM if inter else []))
    rows = flexible_table(q_ls / 1000.0, sizes, fac, rho, mu)

    idx = next((i for i, r in enumerate(rows) if r["V"] <= vm and r["dp"] <= ft), None)
    meets = idx is not None
    if idx is None:
        idx = len(rows) - 1
    rec = rows[idx]

    lo, hi = max(0, idx - 2), min(len(rows), idx + 3)
    near = []
    for i in range(lo, hi):
        r = rows[i]
        sel = i == idx
        near.append(html.Tr(
            [td(f"Ø {r['d']} mm", bold=sel), td(f"{r['V']:.2f} m/s", "right", sel), td(f"{r['dp']:.2f} Pa/m", "right", sel)],
            style={"background": "#eef5ee" if sel else "transparent"},
        ))

    return html.Div(
        [
            html.H3("Recommended flexible duct", style={"margin": 0}),
            html.Div(f"{q_ls:,.0f} L/s · ≤ {ft:g} Pa/m · ≤ {vm:g} m/s", style=HINT),
            html.Div(
                [html.Div("FLEXIBLE DUCT", style={"fontSize": "11px", "letterSpacing": "0.08em", "color": MUTED}),
                 html.Div(f"Ø {rec['d']} mm", style={"fontSize": "40px", "fontWeight": 800, "margin": "4px 0"})],
                style={"textAlign": "center", "padding": "18px", "background": "#f2f6f2",
                       "borderRadius": "10px", "margin": "12px 0"},
            ),
            tile_grid([
                tile("Air velocity", fmt(rec["V"]), "m/s"),
                tile("Pressure loss rate", fmt(rec["dp"], 2), "Pa/m"),
                tile(f"Straight loss over {length_m:g} m", fmt(rec["dp"] * length_m, 1), "Pa"),
            ]),
            banner(meets,
                   "Meets both limits" if meets else "Largest listed size still exceeds a limit",
                   [] if meets else ["Use two ducts in parallel or a rigid duct for this airflow."]),
            banner(False, f"Run is longer than the AWP {FLEX_MAX_LENGTH_M:g} m flexible duct limit",
                   [f"{length_m:g} m is too long. Flexible duct beyond {FLEX_MAX_LENGTH_M:g} m is inefficient and carries "
                    "significant risk. Use rigid duct for the main run."]) if too_long else None,
            html.H4("Nearby listed sizes", style={"margin": "8px 0 4px 0"}),
            html.Table(
                [html.Thead(html.Tr([th("SIZE"), th("VELOCITY", "right"), th("FRICTION", "right")])),
                 html.Tbody(near)],
                style={"width": "100%", "borderCollapse": "collapse"},
            ),
            html.Div(
                "Preliminary guide only. Friction is modelled for a straight, fully extended duct using the ASHRAE "
                "'medium rough' roughness of 0.9 mm, which is conservative compared with some manufacturer charts. "
                "Bends, sag, compression, terminals and entry/exit losses are excluded. "
                "Always confirm against the manufacturer's published data.",
                style={**HINT, "marginTop": "10px"},
            ),
        ],
        style=CARD,
    )