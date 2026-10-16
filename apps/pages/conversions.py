from dash import register_page, html, dcc, Input, Output, dash_table, callback
from apps.shared.ui import section_card, input_box, dropdown, BRAND, MUTED, BLACK
from apps.shared.units import (
    c_to_f, f_to_c, linear_convert,
    velocity_to_base, flow_to_base, pressure_to_base, power_to_base,
    parse_fraction, gauge_to_mm
)

register_page(__name__, path="/conversions", name="Conversions")

layout = html.Div(
    style={"width": "100%", "margin": "20px auto", "fontFamily": "Segoe UI, Inter, Arial", "color": BLACK},
    children=[
        html.Div(style={"display": "flex", "alignItems": "center", "gap": "10px", "marginBottom": "18px"}, children=[
            html.Div(style={"width": "12px", "height": "32px", "backgroundColor": BRAND, "borderRadius": "6px"}),
            html.H1("Conversions", style={"margin": "0", "fontSize": "28px"}),
        ]),
        html.P("Quick reference with on-page calculators.", style={"color": MUTED, "marginTop": "0"}),

        html.Div(style={"display": "grid", "gridTemplateColumns": "1fr", "gap": "18px"}, children=[
            # Temperature
            section_card(
                "Temperature",
                ["T °C = (T °F – 32) × 5/9", "T °F = (T °C × 9/5) + 32"],
                controls_row=[
                    dcc.Input(id="temp-value", type="number", value=0.0,
                              style={"width": "140px", "padding": "10px 12px", "borderRadius": "10px", "border": "1px solid #d9d9d9"}),
                    dropdown("temp-from", ["°C", "°F"], "°C", "120px"),
                    html.Div("→", style={"fontWeight": "700"}),
                    dropdown("temp-to", ["°C", "°F"], "°F", "120px"),
                ],
                result_id="temp-result"
            ),

            # Velocity
            section_card(
                "Velocity",
                ["1 ft/s = 0.3048 m/s   •   1 m/s = 3.28 ft/s",
                 "1 ft/min = 0.00508 m/s   •   1 m/s = 196.8 fpm",
                 "1 mile/hr = 1.61 km/hr   •   1 km/hr = 0.621 mph"],
                controls_row=[
                    dcc.Input(id="vel-value", type="number", value=1.0,
                              style={"width": "140px", "padding": "10px 12px", "borderRadius": "10px", "border": "1px solid #d9d9d9"}),
                    dropdown("vel-from", velocity_to_base.keys(), "m/s"),
                    html.Div("→", style={"fontWeight": "700"}),
                    dropdown("vel-to", velocity_to_base.keys(), "ft/s"),
                ],
                result_id="vel-result"
            ),

            # Volume Flow Rate
            section_card(
                "Volume Flow Rate",
                ["1 CFM = 0.472 L/s", "1 L/s = 2.12 CFM"],
                controls_row=[
                    dcc.Input(id="flow-value", type="number", value=1.0,
                              style={"width": "140px", "padding": "10px 12px", "borderRadius": "10px", "border": "1px solid #d9d9d9"}),
                    dropdown("flow-from", flow_to_base.keys(), "L/s"),
                    html.Div("→", style={"fontWeight": "700"}),
                    dropdown("flow-to", flow_to_base.keys(), "CFM"),
                ],
                result_id="flow-result"
            ),

            # Pressure
            section_card(
                "Pressure",
                ["1 psi = 6.895 kPa   •   1 kPa = 0.145 psi",
                 "1 in H₂O = 249 Pa   •   1 mm H₂O = 9.81 Pa",
                 "1 in Hg = 3.39 kPa   •   1 mm Hg = 133.3 Pa",
                 "1 bar = 100 kPa   •   1 Std. Atmos. = 101.3 kPa = 760 mm Hg Abs"],
                controls_row=[
                    dcc.Input(id="press-value", type="number", value=1.0,
                              style={"width": "140px", "padding": "10px 12px", "borderRadius": "10px", "border": "1px solid #d9d9d9"}),
                    dropdown("press-from", pressure_to_base.keys(), "kPa"),
                    html.Div("→", style={"fontWeight": "700"}),
                    dropdown("press-to", pressure_to_base.keys(), "psi"),
                ],
                result_id="press-result"
            ),

            # Power / Heat Flow Rate
            section_card(
                "Power & Heat Flow Rate",
                ["1 HP = 0.746 kW   •   1 kW = 1.34 HP",
                 "1 Btu/hr = 0.293 W   •   1 kW = 3415 Btu/hr",
                 "1 ton refriger. = 3.517 kW   •   1 kW = 0.284 ton refriger.",
                 "1 MJ/hr = 278 W   •   1 kW = 3.6 MJ/hr"],
                controls_row=[
                    dcc.Input(id="power-value", type="number", value=1.0,
                              style={"width": "140px", "padding": "10px 12px", "borderRadius": "10px", "border": "1px solid #d9d9d9"}),
                    dropdown("power-from", power_to_base.keys(), "kW"),
                    html.Div("→", style={"fontWeight": "700"}),
                    dropdown("power-to", power_to_base.keys(), "HP"),
                ],
                result_id="power-result"
            ),

            # Length
            section_card(
                "Length",
                ["1 inch = 25.4 mm", "1 mm = 0.03937 in"],
                controls_row=[
                    dcc.Input(id="len-value", type="text", value="3 1/8",
                              style={"width": "160px", "padding": "10px 12px", "borderRadius": "10px", "border": "1px solid #d9d9d9"}),
                    dropdown("len-from", ["in", "mm"], "in", "120px"),
                    html.Div("→", style={"fontWeight": "700"}),
                    dropdown("len-to", ["mm", "in"], "mm", "120px"),
                ],
                result_id="len-result"
            ),

            # Galvanised gauge
            section_card(
                "Galvanised Metal Gauge Conversions",
                ["Gauge numbers (Imperial) to sheet thickness (Metric mm)."],
                controls_row=[
                    dropdown("gauge-from", list(gauge_to_mm.keys()), "20 #", "140px"),
                    html.Div("→", style={"fontWeight": "700"}),
                    html.Div(id="gauge-result", style={"fontWeight": "600"})
                ],
                result_id="gauge-dummy",
                extra_children=dash_table.DataTable(
                    columns=[{"name": "Imperial", "id": "imperial"},
                             {"name": "Metric", "id": "metric"}],
                    data=[{"imperial": k, "metric": f"{v} mm"} for k, v in gauge_to_mm.items()],
                    style_cell={"padding": "8px", "textAlign": "center"},
                    style_header={"backgroundColor": "#f5f5f5", "fontWeight": "bold"},
                    style_table={"margin": "12px auto", "width": "60%", "borderRadius": "10px", "overflow": "hidden"},
                )
            ),
        ]),
        html.Div("AWP • Mechanical Handbook", style={"textAlign": "center", "color": "#5f6368", "marginTop": "22px"})
    ]
)

# ---------- callbacks ----------
@callback(Output("temp-result", "children"),
          Input("temp-value", "value"), Input("temp-from", "value"), Input("temp-to", "value"))
def convert_temp(val, u_from, u_to):
    if val is None or u_from is None or u_to is None: return ""
    if u_from == u_to:
        out = val
    elif u_from == "°C" and u_to == "°F":
        out = c_to_f(val)
    elif u_from == "°F" and u_to == "°C":
        out = f_to_c(val)
    else:
        return "Unsupported"
    return f"= {out:,.6g} {u_to}"

@callback(Output("vel-result", "children"),
          Input("vel-value", "value"), Input("vel-from", "value"), Input("vel-to", "value"))
def convert_vel(val, u_from, u_to):
    if val is None or u_from is None or u_to is None: return ""
    out = linear_convert(val, velocity_to_base, u_from, u_to)
    return f"= {out:,.6g} {u_to}"

@callback(Output("flow-result", "children"),
          Input("flow-value", "value"), Input("flow-from", "value"), Input("flow-to", "value"))
def convert_flow(val, u_from, u_to):
    if val is None or u_from is None or u_to is None: return ""
    out = linear_convert(val, flow_to_base, u_from, u_to)
    return f"= {out:,.6g} {u_to}"

@callback(Output("press-result", "children"),
          Input("press-value", "value"), Input("press-from", "value"), Input("press-to", "value"))
def convert_press(val, u_from, u_to):
    if val is None or u_from is None or u_to is None: return ""
    out = linear_convert(val, pressure_to_base, u_from, u_to)
    return f"= {out:,.6g} {u_to}"

@callback(Output("power-result", "children"),
          Input("power-value", "value"), Input("power-from", "value"), Input("power-to", "value"))
def convert_power(val, u_from, u_to):
    if val is None or u_from is None or u_to is None: return ""
    out = linear_convert(val, power_to_base, u_from, u_to)
    return f"= {out:,.6g} {u_to}"

@callback(Output("len-result", "children"),
          Input("len-value", "value"), Input("len-from", "value"), Input("len-to", "value"))
def convert_length(val_txt, u_from, u_to):
    if val_txt is None or u_from is None or u_to is None: return ""
    try:
        if u_from == "in":
            inches = parse_fraction(val_txt)
            mm = inches * 25.4
        else:
            mm = float(str(val_txt).strip())
            inches = mm / 25.4
    except Exception:
        return "Enter a valid number (e.g. 3 1/8, 1/8, 3.125, or 10)."
    if u_to == "mm":
        return f"= {mm:,.6g} mm"
    dec = inches
    sixteenth = round(dec * 16)
    whole = sixteenth // 16
    rem = sixteenth % 16
    frac_str = f"{int(rem)}/16" if rem else ""
    mixed = f'{int(whole)} {frac_str}"'.strip()
    return f'= {dec:,.6g} in  ({mixed})'

@callback(Output("gauge-result", "children"),
          Input("gauge-from", "value"))
def convert_gauge(gauge_sel):
    if not gauge_sel: return ""
    mm = gauge_to_mm[gauge_sel]
    return f"= {mm} mm"
