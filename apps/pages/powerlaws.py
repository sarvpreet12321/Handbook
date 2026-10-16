# apps/pages/equations.py
from dash import register_page, html, dcc, Input, Output, dash_table, callback
from apps.shared.ui import section_card, input_box, dropdown, BRAND, MUTED, BLACK

register_page(__name__, path="/powerlaws", name="powerlaws")

layout = html.Div(
    style={
        "width": "100%",
        "margin": "20px auto",
        "fontFamily": "Segoe UI, Inter, Arial",
        "color": BLACK,
    },
    children=[
        # Page header
        html.Div(
            style={"display": "flex", "alignItems": "center", "gap": "20px", "marginBottom": "18px"},
            children=[
                html.Div(
                    style={"width": "12px", "height": "32px", "backgroundColor": BRAND, "borderRadius": "6px"}
                ),
                html.H1("Power Laws", style={"margin": "0", "fontSize": "28px"}),
            ],
        ),
        html.P("Quick calculators for common power equations.", style={"color": MUTED, "marginTop": 0}),

        # --- all cards in one flex column ---
        html.Div(
            style={"display": "flex", "flexDirection": "column", "gap": "30px"},
            children=[
                # --- Power = V × I ---
                section_card(
                    "Power from Voltage and Current",
                    [],  # bullets
                    [
                        html.Div(
                            dcc.Markdown(
                                r"$$P\,(W) = V \times I$$",
                                mathjax=True,
                                style={"textAlign": "center", "width": "100%", "marginBottom": "15px"},
                            ),
                            style={"width": "100%"},
                        ),
                        html.Div(
                            [
                                html.Label("Voltage (V)"),
                                input_box("voltage-vi", 100.0, step=1, width="140px"),
                            ],
                            style={"display": "flex", "flexDirection": "column"},
                        ),
                        html.Div(
                            [
                                html.Label("Current (I)"),
                                input_box("current-vi", 5.0, step=0.5, width="140px"),
                            ],
                            style={"display": "flex", "flexDirection": "column"},
                        ),
                    ],
                    result_id="power-vi",
                ),

                # --- Power = V² / R ---
                section_card(
                    "Power from Voltage and Resistance",
                    [],  # bullets
                    [
                        html.Div(
                            dcc.Markdown(
                                r"$$P\,(W) = \frac{V^2}{R}$$",
                                mathjax=True,
                                style={"textAlign": "center", "width": "100%", "marginBottom": "15px"},
                            ),
                            style={"width": "100%"},
                        ),
                        html.Div(
                            [
                                html.Label("Voltage (V)"),
                                input_box("voltage-v2r", 100.0, step=1, width="140px"),
                            ],
                            style={"display": "flex", "flexDirection": "column"},
                        ),
                        html.Div(
                            [
                                html.Label("Resistance (Ω)"),
                                input_box("resistance-v2r", 20.0, step=0.5, width="140px"),
                            ],
                            style={"display": "flex", "flexDirection": "column"},
                        ),
                    ],
                    result_id="power-v2r",
                ),

                # --- Power = I² R ---
                section_card(
                    "Power from Current and Resistance",
                    [],  # bullets
                    [
                        html.Div(
                            dcc.Markdown(
                                r"$$P\,(W) = I^2 \times R$$",
                                mathjax=True,
                                style={"textAlign": "center", "width": "100%", "marginBottom": "15px"},
                            ),
                            style={"width": "100%"},
                        ),
                        html.Div(
                            [
                                html.Label("Current (I)"),
                                input_box("current-i2r", 10.0, step=0.5, width="140px"),
                            ],
                            style={"display": "flex", "flexDirection": "column"},
                        ),
                        html.Div(
                            [
                                html.Label("Resistance (Ω)"),
                                input_box("resistance-i2r", 5.0, step=0.5, width="140px"),
                            ],
                            style={"display": "flex", "flexDirection": "column"},
                        ),
                    ],
                    result_id="power-i2r",
                ),
            ],
        ),

        # Footer
        html.Div(
            "AWP • Mechanical Handbook",
            style={"textAlign": "center", "color": "#5f6368", "marginTop": "22px"},
        ),
    ],
)

# --------- Callbacks ---------

@callback(
    Output("power-vi", "children"),
    Input("voltage-vi", "value"),
    Input("current-vi", "value"),
)
def calc_power_vi(V, I):
    try:
        if V is None or I is None:
            return ""
        power = float(V) * float(I)
        return f"Power = {power:,.2f} W"
    except Exception:
        return ""

@callback(
    Output("power-v2r", "children"),
    Input("voltage-v2r", "value"),
    Input("resistance-v2r", "value"),
)
def calc_power_v2r(V, R):
    try:
        if V is None or R is None or float(R) == 0.0:
            return ""
        power = (float(V) ** 2) / float(R)
        return f"Power = {power:,.2f} W"
    except Exception:
        return ""

@callback(
    Output("power-i2r", "children"),
    Input("current-i2r", "value"),
    Input("resistance-i2r", "value"),
)
def calc_power_i2r(I, R):
    try:
        if I is None or R is None:
            return ""
        power = (float(I) ** 2) * float(R)
        return f"Power = {power:,.2f} W"
    except Exception:
        return ""
