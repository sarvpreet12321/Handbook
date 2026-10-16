# apps/pages/pumplaws.py
from dash import register_page, html, dcc, Input, Output, callback, dash_table
from apps.shared.ui import section_card, input_box, BRAND, MUTED, BLACK

register_page(__name__, path="/pumplaws", name="pumplaws")

# ---------------- Nomenclature table ----------------
nomenclature_rows = [
    {"Symbol": "q", "Meaning": "Flow rate", "Units": "l/s"},    
    {"Symbol": "n", "Meaning": "Pump impeller speed", "Units": "rpm"},
    {"Symbol": "d", "Meaning": "Impeller diameter", "Units": "mm"},
    {"Symbol": "H", "Meaning": "Head pressure", "Units": "m"},
    {"Symbol": "P", "Meaning": "Power input", "Units": "kW"},   
    {"Symbol": "V", "Meaning": "Velocity of flow", "Units": "m/s"},
]

layout = html.Div(
    style={"width": "100%", "margin": "20px auto", "fontFamily": "Segoe UI, Inter, Arial", "color": BLACK},
    children=[
        # Header
        html.Div(
            style={"display": "flex", "alignItems": "center", "gap": "20px", "marginBottom": "18px"},
            children=[
                html.Div(style={"width": "12px", "height": "32px", "backgroundColor": BRAND, "borderRadius": "6px"}),
                html.H1("Pump Laws", style={"margin": "0", "fontSize": "28px"}),
            ],
        ),
        html.P(
            "The pump affinity laws can be used to predict the performance of a pump at different diameters for the same speed and different speed for the same diameter. "
            "Can be usefully applied to small changes made to geometrically similar pumps.",
            style={"color": MUTED, "marginTop": 0},
        ),

        # Nomenclature table
        html.Div(
            style={"marginTop": "20px"},
            children=[
                html.H3("Nomenclature", style={"marginTop": "20px","marginBottom": "40px"}),
                dash_table.DataTable(
                    id="fanlaws-nomenclature",
                    data=nomenclature_rows,
                    columns=[{"name": "Symbol", "id": "Symbol"},
                             {"name": "Meaning", "id": "Meaning"},
                             {"name": "Units", "id": "Units"}],
                    style_cell={"padding": "8px", "fontFamily": "Segoe UI, Inter, Arial", "textAlign": "center"},
                    style_header={"fontWeight": "600", "backgroundColor": "#f5f5f5", "textAlign": "center"},
                    style_as_list_view=True,
                    page_size=20,
                ),
            ],
        ),

        # Cards
        html.Div(
            style={"display": "flex", "flexDirection": "column", "gap": "30px"},
            children=[

                # 1) Flow rate scaling
                section_card(
                    "1) Flow Rate Scaling",
                    ["Volume flow can scale with speed or impeller diameter changes."],
                    [
                        # Speed scaling block
                        html.Div(
                            style={"border": "1px solid #ccc", "padding": "12px", "marginBottom": "16px", "borderRadius": "8px"},
                            children=[
                                html.H4("Speed Scaling"),
                                dcc.Markdown(r"$$q_2 = q_1 \left(\frac{n_2}{n_1}\right)$$",
                                             mathjax=True, style={"textAlign": "center", "marginBottom": "12px"}),
                                html.Div([
                                    html.Div([html.Label("q₁ (l/s)"), input_box("q_speed_1", 1.00, step=0.01, width="140px")],
                                             style={"display": "flex", "flexDirection": "column"}),
                                    html.Div([html.Label("n₁ (rpm)"), input_box("q_n1", 2200.0, step=0.1, width="140px")],
                                             style={"display": "flex", "flexDirection": "column"}),
                                    html.Div([html.Label("n₂ (rpm)"), input_box("q_n2", 2400.0, step=0.1, width="140px")],
                                             style={"display": "flex", "flexDirection": "column"}),
                                ], style={"display": "flex", "gap": "18px", "flexWrap": "wrap"}),
                                html.Div(id="q_speed_2_result", style={"marginTop": "12px", "fontWeight": "bold"}),
                            ]
                        ),

                        # Diameter scaling block
                        html.Div(
                            style={"border": "1px solid #ccc", "padding": "12px", "borderRadius": "8px"},
                            children=[
                                html.H4("Diameter Scaling"),
                                dcc.Markdown(r"$$q_2 = q_1 \left(\frac{d_2}{d_1}\right)^2$$",
                                             mathjax=True, style={"textAlign": "center", "marginBottom": "12px"}),
                                html.Div([
                                    html.Div([html.Label("q₁ (l/s)"), input_box("q_diam_1", 1.00, step=0.01, width="140px")],
                                             style={"display": "flex", "flexDirection": "column"}),
                                    html.Div([html.Label("d₁ (mm)"), input_box("q_d1", 190.0, step=1, width="140px")],
                                             style={"display": "flex", "flexDirection": "column"}),
                                    html.Div([html.Label("d₂ (mm)"), input_box("q_d2", 200.0, step=1, width="140px")],
                                             style={"display": "flex", "flexDirection": "column"}),
                                ], style={"display": "flex", "gap": "18px", "flexWrap": "wrap"}),
                                html.Div(id="q_diam_2_result", style={"marginTop": "12px", "fontWeight": "bold"}),
                            ]
                        ),
                    ],
                    result_id="dummy",
                ),

                # 2) Head Pressure Scaling
                section_card(
                    "2) Head Pressure Scaling",
                    ["Head pressure scales with speed or impeller diameter changes."],
                    [
                        html.Div(
                            style={"border": "1px solid #ccc", "padding": "12px", "marginBottom": "16px", "borderRadius": "8px"},
                            children=[
                                html.H4("Speed Scaling"),
                                dcc.Markdown(r"$$H_2 = H_1 \left(\frac{n_2}{n_1}\right)^2$$",
                                             mathjax=True, style={"textAlign": "center", "marginBottom": "12px"}),
                                html.Div([
                                    html.Div([html.Label("H₁ (m)"), input_box("H_speed_1", 10.0, step=0.1, width="140px")],
                                             style={"display": "flex", "flexDirection": "column"}),
                                    html.Div([html.Label("n₁ (rpm)"), input_box("H_n1", 2200.0, step=0.1, width="140px")],
                                             style={"display": "flex", "flexDirection": "column"}),
                                    html.Div([html.Label("n₂ (rpm)"), input_box("H_n2", 2400.0, step=0.1, width="140px")],
                                             style={"display": "flex", "flexDirection": "column"}),
                                ], style={"display": "flex", "gap": "18px", "flexWrap": "wrap"}),
                                html.Div(id="H_speed_2_result", style={"marginTop": "12px", "fontWeight": "bold"}),
                            ]
                        ),
                        html.Div(
                            style={"border": "1px solid #ccc", "padding": "12px", "borderRadius": "8px"},
                            children=[
                                html.H4("Diameter Scaling"),
                                dcc.Markdown(r"$$H_2 = H_1 \left(\frac{d_2}{d_1}\right)^2$$",
                                             mathjax=True, style={"textAlign": "center", "marginBottom": "12px"}),
                                html.Div([
                                    html.Div([html.Label("H₁ (m)"), input_box("H_diam_1", 10.0, step=0.1, width="140px")],
                                             style={"display": "flex", "flexDirection": "column"}),
                                    html.Div([html.Label("d₁ (mm)"), input_box("H_d1", 190.0, step=1, width="140px")],
                                             style={"display": "flex", "flexDirection": "column"}),
                                    html.Div([html.Label("d₂ (mm)"), input_box("H_d2", 200.0, step=1, width="140px")],
                                             style={"display": "flex", "flexDirection": "column"}),
                                ], style={"display": "flex", "gap": "18px", "flexWrap": "wrap"}),
                                html.Div(id="H_diam_2_result", style={"marginTop": "12px", "fontWeight": "bold"}),
                            ]
                        ),
                    ],
                    result_id="dummy",
                ),

                # 3) Input Power Scaling
                section_card(
                    "3) Input Power Scaling",
                    ["Power input scales with speed or impeller diameter changes."],
                    [
                        html.Div(
                            style={"border": "1px solid #ccc", "padding": "12px", "marginBottom": "16px", "borderRadius": "8px"},
                            children=[
                                html.H4("Speed Scaling"),
                                dcc.Markdown(r"$$P_2 = P_1 \left(\frac{n_2}{n_1}\right)^3$$",
                                             mathjax=True, style={"textAlign": "center", "marginBottom": "12px"}),
                                html.Div([
                                    html.Div([html.Label("P₁ (kW)"), input_box("P_speed_1", 5.0, step=0.1, width="140px")],
                                             style={"display": "flex", "flexDirection": "column"}),
                                    html.Div([html.Label("n₁ (rpm)"), input_box("P_n1", 2200.0, step=0.1, width="140px")],
                                             style={"display": "flex", "flexDirection": "column"}),
                                    html.Div([html.Label("n₂ (rpm)"), input_box("P_n2", 2400.0, step=0.1, width="140px")],
                                             style={"display": "flex", "flexDirection": "column"}),
                                ], style={"display": "flex", "gap": "18px", "flexWrap": "wrap"}),
                                html.Div(id="P_speed_2_result", style={"marginTop": "12px", "fontWeight": "bold"}),
                            ]
                        ),
                        html.Div(
                            style={"border": "1px solid #ccc", "padding": "12px", "borderRadius": "8px"},
                            children=[
                                html.H4("Diameter Scaling"),
                                dcc.Markdown(r"$$P_2 = P_1 \left(\frac{d_2}{d_1}\right)^5$$",
                                             mathjax=True, style={"textAlign": "center", "marginBottom": "12px"}),
                                html.Div([
                                    html.Div([html.Label("P₁ (kW)"), input_box("P_diam_1", 5.0, step=0.1, width="140px")],
                                             style={"display": "flex", "flexDirection": "column"}),
                                    html.Div([html.Label("d₁ (mm)"), input_box("P_d1", 190.0, step=1, width="140px")],
                                             style={"display": "flex", "flexDirection": "column"}),
                                    html.Div([html.Label("d₂ (mm)"), input_box("P_d2", 200.0, step=1, width="140px")],
                                             style={"display": "flex", "flexDirection": "column"}),
                                ], style={"display": "flex", "gap": "18px", "flexWrap": "wrap"}),
                                html.Div(id="P_diam_2_result", style={"marginTop": "12px", "fontWeight": "bold"}),
                            ]
                        ),
                    ],
                    result_id="dummy",
                ),

                html.Div("AWP • Mechanical Handbook", style={"textAlign": "center", "color": "#5f6368", "marginTop": "22px"}),
            ],
        ),
    ],
)

# -------------------- Callbacks --------------------
@callback(
    Output("q_speed_2_result", "children"),
    Output("q_diam_2_result", "children"),
    Output("H_speed_2_result", "children"),
    Output("H_diam_2_result", "children"),
    Output("P_speed_2_result", "children"),
    Output("P_diam_2_result", "children"),
    Input("q_speed_1", "value"),
    Input("q_n1", "value"),
    Input("q_n2", "value"),
    Input("q_diam_1", "value"),
    Input("q_d1", "value"),
    Input("q_d2", "value"),
    Input("H_speed_1", "value"),
    Input("H_n1", "value"),
    Input("H_n2", "value"),
    Input("H_diam_1", "value"),
    Input("H_d1", "value"),
    Input("H_d2", "value"),
    Input("P_speed_1", "value"),
    Input("P_n1", "value"),
    Input("P_n2", "value"),
    Input("P_diam_1", "value"),
    Input("P_d1", "value"),
    Input("P_d2", "value"),
)
def calc_all(
    q_speed_1, q_n1, q_n2, q_diam_1, q_d1, q_d2,
    H_speed_1, H_n1, H_n2, H_diam_1, H_d1, H_d2,
    P_speed_1, P_n1, P_n2, P_diam_1, P_d1, P_d2
):
    # Convert mm to meters for calculations
    try:
        q_d1_m, q_d2_m = float(q_d1)/1000, float(q_d2)/1000
        q_diam_2 = float(q_diam_1) * (q_d2_m / q_d1_m)**2
        q_diam_text = f"q₂ = {q_diam_2:,.4f} l/s"
    except Exception:
        q_diam_text = "Invalid input for diameter scaling"

    try:
        H_d1_m, H_d2_m = float(H_d1)/1000, float(H_d2)/1000
        H_diam_2 = float(H_diam_1) * (H_d2_m / H_d1_m)**2
        H_diam_text = f"H₂ = {H_diam_2:,.4f} m"
    except Exception:
        H_diam_text = "Invalid input for diameter scaling"

    try:
        P_d1_m, P_d2_m = float(P_d1)/1000, float(P_d2)/1000
        P_diam_2 = float(P_diam_1) * (P_d2_m / P_d1_m)**5
        P_diam_text = f"P₂ = {P_diam_2:,.4f} kW"
    except Exception:
        P_diam_text = "Invalid input for diameter scaling"

    # Speed scaling
    try:
        q_speed_2 = float(q_speed_1) * (float(q_n2)/float(q_n1))
        q_speed_text = f"q₂ = {q_speed_2:,.4f} l/s"
    except Exception:
        q_speed_text = "Invalid input for speed scaling"

    try:
        H_speed_2 = float(H_speed_1) * (float(H_n2)/float(H_n1))**2
        H_speed_text = f"H₂ = {H_speed_2:,.4f} m"
    except Exception:
        H_speed_text = "Invalid input for speed scaling"

    try:
        P_speed_2 = float(P_speed_1) * (float(P_n2)/float(P_n1))**3
        P_speed_text = f"P₂ = {P_speed_2:,.4f} kW"
    except Exception:
        P_speed_text = "Invalid input for speed scaling"

    return (
        html.Div(q_speed_text),
        html.Div(q_diam_text),
        html.Div(H_speed_text),
        html.Div(H_diam_text),
        html.Div(P_speed_text),
        html.Div(P_diam_text),
    )
