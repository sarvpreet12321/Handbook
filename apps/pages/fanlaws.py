# apps/pages/fanlaws.py
from math import log10
from dash import register_page, html, dcc, Input, Output, callback, dash_table
from apps.shared.ui import section_card, input_box, BRAND, MUTED, BLACK

register_page(__name__, path="/fanlaws", name="fanlaws")

# ---------------- Nomenclature table ----------------
nomenclature_rows = [
    {"Symbol": "qᵥ",   "Meaning": "Volume flow of air",              "Units": "m³/s"},    # q_v → qᵥ
    {"Symbol": "n",     "Meaning": "Rotational speed of fan",         "Units": "rev/s"},
    {"Symbol": "d",     "Meaning": "Diameter of fan",                 "Units": "m"},
    {"Symbol": "p",     "Meaning": "Pressure developed by the fan",   "Units": "Pa"},
    {"Symbol": "ρ",     "Meaning": "Density of air",                  "Units": "kg/m³"},   # rho
    {"Symbol": "Pᵣ",    "Meaning": "Power absorbed by the fan",       "Units": "kW"},      # P_R → Pᴿ
    {"Symbol": "B",     "Meaning": "Barometric pressure",             "Units": "mbar"},
    {"Symbol": "T",     "Meaning": "Absolute temperature",            "Units": "K = °C + 273"},
    {"Symbol": "pₜF",   "Meaning": "Fan total pressure",              "Units": "Pa"},      # p_tF → pₜF
    {"Symbol": "pₛF",   "Meaning": "Fan static pressure",             "Units": "Pa"},      # p_sF → pₛF
    {"Symbol": "p_d",   "Meaning": "System dynamic/velocity pressure","Units": "Pa"},      # subscript d
    {"Symbol": "V",     "Meaning": "Velocity of air",                 "Units": "m/s"},
    {"Symbol": "PWL",   "Meaning": "Sound power level",               "Units": "dB"},
]

layout = html.Div(
    style={
        "width": "100%",
        "margin": "20px auto",
        "fontFamily": "Segoe UI, Inter, Arial",
        "color": BLACK,
    },
    children=[
        # Header
        html.Div(
            style={"display": "flex", "alignItems": "center", "gap": "20px", "marginBottom": "18px"},
            children=[
                html.Div(style={"width": "12px", "height": "32px", "backgroundColor": BRAND, "borderRadius": "6px"}),
                html.H1("Fan Laws", style={"margin": "0", "fontSize": "28px"}),
            ],
        ),
        html.P(
            "Quick calculators for the classic fan affinity laws and related corrections. "
            "Assumes geometrically similar fans where noted.",
            style={"color": MUTED, "marginTop": 0},
        ),

        html.Div(
            style={"marginTop": "20px"},
            children=[
                html.H3("Nomenclature", style={"marginTop": "20px","marginBottom": "40px"}),
                dash_table.DataTable(
                    id="fanlaws-nomenclature",
                    data=nomenclature_rows,
                    columns=[
                        {"name": "Symbol", "id": "Symbol"},
                        {"name": "Meaning", "id": "Meaning"},
                        {"name": "Units",  "id": "Units"},
                    ],
                    style_cell={
                        "padding": "8px",
                        "fontFamily": "Segoe UI, Inter, Arial",
                        "textAlign": "center",      # <--- center values
                    },
                    style_header={
                        "fontWeight": "600",
                        "backgroundColor": "#f5f5f5",
                        "textAlign": "center",     
                    },
                    style_as_list_view=True,
                    page_size=20,
                ),
            ],
        ),

        # Cards
        html.Div(
            style={"display": "flex", "flexDirection": "column", "gap": "30px"},
            children=[

                # 1) Volume flow scaling
                section_card(
                    "1) Volume Flow Scaling",
                    ["Scales flow rate when fan speed or diameter changes (geometrically similar fans)."],
                    [
                        html.Div(
                            dcc.Markdown(
                                r"$$q_2 = q_1 \left(\frac{n_2}{n_1}\right)\left(\frac{d_2}{d_1}\right)^3$$",
                                mathjax=True,
                                style={"textAlign": "center", "width": "100%", "marginBottom": "12px"},
                            ),
                            style={"width": "100%"},
                        ),
                        html.Div([
                            html.Div([html.Label("q₁ (m³/s)"), input_box("q1", 1.00, step=0.01, width="140px")],
                                     style={"display": "flex", "flexDirection": "column"}),
                            html.Div([html.Label("n₁ (rev/s)"), input_box("n1", 20.0, step=0.1, width="140px")],
                                     style={"display": "flex", "flexDirection": "column"}),
                            html.Div([html.Label("n₂ (rev/s)"), input_box("n2", 25.0, step=0.1, width="140px")],
                                     style={"display": "flex", "flexDirection": "column"}),
                            html.Div([html.Label("d₁ (m)"),     input_box("d1", 0.5, step=0.01, width="140px")],
                                     style={"display": "flex", "flexDirection": "column"}),
                            html.Div([html.Label("d₂ (m)"),     input_box("d2", 0.5, step=0.01, width="140px")],
                                     style={"display": "flex", "flexDirection": "column"}),
                        ], style={"display": "flex", "gap": "18px", "flexWrap": "wrap"}),
                    ],
                    result_id="q2",
                ),

                # 2) Pressure scaling
                section_card(
                    "2) Pressure Scaling",
                    ["Scales fan pressure with speed, diameter, and density."],
                    [
                        html.Div(
                            dcc.Markdown(
                                r"$$p_2 = p_1 \left(\frac{n_2}{n_1}\right)^2\left(\frac{d_2}{d_1}\right)^2\left(\frac{\rho_2}{\rho_1}\right)$$",
                                mathjax=True,
                                style={"textAlign": "center", "width": "100%", "marginBottom": "12px"},
                            ),
                            style={"width": "100%"},
                        ),
                        html.Div([
                            html.Div([html.Label("p₁ (Pa)"),    input_box("p1", 300.0, step=1, width="140px")],
                                     style={"display": "flex", "flexDirection": "column"}),
                            html.Div([html.Label("n₁ (rev/s)"), input_box("n1_p", 20.0, step=0.1, width="140px")],
                                     style={"display": "flex", "flexDirection": "column"}),
                            html.Div([html.Label("n₂ (rev/s)"), input_box("n2_p", 25.0, step=0.1, width="140px")],
                                     style={"display": "flex", "flexDirection": "column"}),
                            html.Div([html.Label("d₁ (m)"),     input_box("d1_p", 0.5, step=0.01, width="140px")],
                                     style={"display": "flex", "flexDirection": "column"}),
                            html.Div([html.Label("d₂ (m)"),     input_box("d2_p", 0.5, step=0.01, width="140px")],
                                     style={"display": "flex", "flexDirection": "column"}),
                            html.Div([html.Label("ρ₁ (kg/m³)"), input_box("rho1_p", 1.20, step=0.01, width="140px")],
                                     style={"display": "flex", "flexDirection": "column"}),
                            html.Div([html.Label("ρ₂ (kg/m³)"), input_box("rho2_p", 1.20, step=0.01, width="140px")],
                                     style={"display": "flex", "flexDirection": "column"}),
                        ], style={"display": "flex", "gap": "18px", "flexWrap": "wrap"}),
                    ],
                    result_id="p2",
                ),

                # 3) Absorbed power scaling
                section_card(
                    "3) Absorbed Power Scaling",
                    ["Scales input/absorbed power with speed, diameter, and density."],
                    [
                        html.Div(
                            dcc.Markdown(
                                r"$$P_2 = P_1 \left(\frac{n_2}{n_1}\right)^3\left(\frac{d_2}{d_1}\right)^5\left(\frac{\rho_2}{\rho_1}\right)$$",
                                mathjax=True,
                                style={"textAlign": "center", "width": "100%", "marginBottom": "12px"},
                            ),
                            style={"width": "100%"},
                        ),
                        html.Div([
                            html.Div([html.Label("P₁ (kW)"),    input_box("P1", 5.0, step=0.1, width="140px")],
                                     style={"display": "flex", "flexDirection": "column"}),
                            html.Div([html.Label("n₁ (rev/s)"), input_box("n1_P", 20.0, step=0.1, width="140px")],
                                     style={"display": "flex", "flexDirection": "column"}),
                            html.Div([html.Label("n₂ (rev/s)"), input_box("n2_P", 25.0, step=0.1, width="140px")],
                                     style={"display": "flex", "flexDirection": "column"}),
                            html.Div([html.Label("d₁ (m)"),     input_box("d1_P", 0.5, step=0.01, width="140px")],
                                     style={"display": "flex", "flexDirection": "column"}),
                            html.Div([html.Label("d₂ (m)"),     input_box("d2_P", 0.5, step=0.01, width="140px")],
                                     style={"display": "flex", "flexDirection": "column"}),
                            html.Div([html.Label("ρ₁ (kg/m³)"), input_box("rho1_P", 1.20, step=0.01, width="140px")],
                                     style={"display": "flex", "flexDirection": "column"}),
                            html.Div([html.Label("ρ₂ (kg/m³)"), input_box("rho2_P", 1.20, step=0.01, width="140px")],
                                     style={"display": "flex", "flexDirection": "column"}),
                        ], style={"display": "flex", "gap": "18px", "flexWrap": "wrap"}),
                    ],
                    result_id="P2",
                ),

                # 4) Sound power level delta
                section_card(
                    "4) Sound Power Level Change",
                    ["Estimated change in sound power level with diameter, speed, and speed of sound."],
                    [
                        html.Div(
                            dcc.Markdown(
                                r"$$\Delta PWL = 70\log_{10}\!\left(\frac{d_2}{d_1}\right)"
                                r"+ 55\log_{10}\!\left(\frac{n_2}{n_1}\right)"
                                r"+ 20\log_{10}\!\left(\frac{c_2}{c_1}\right)$$",
                                mathjax=True,
                                style={"textAlign": "center", "width": "100%", "marginBottom": "12px"},
                            ),
                            style={"width": "100%"},
                        ),
                        html.Div([
                            html.Div([html.Label("d₁ (m)"),     input_box("d1_spl", 0.5, step=0.01, width="140px")],
                                     style={"display": "flex", "flexDirection": "column"}),
                            html.Div([html.Label("d₂ (m)"),     input_box("d2_spl", 0.5, step=0.01, width="140px")],
                                     style={"display": "flex", "flexDirection": "column"}),
                            html.Div([html.Label("n₁ (rev/s)"), input_box("n1_spl", 20.0, step=0.1, width="140px")],
                                     style={"display": "flex", "flexDirection": "column"}),
                            html.Div([html.Label("n₂ (rev/s)"), input_box("n2_spl", 25.0, step=0.1, width="140px")],
                                     style={"display": "flex", "flexDirection": "column"}),
                            html.Div([html.Label("c₁ (m/s)"),   input_box("c1_spl", 343.0, step=1, width="140px")],
                                     style={"display": "flex", "flexDirection": "column"}),
                            html.Div([html.Label("c₂ (m/s)"),   input_box("c2_spl", 343.0, step=1, width="140px")],
                                     style={"display": "flex", "flexDirection": "column"}),
                        ], style={"display": "flex", "gap": "18px", "flexWrap": "wrap"}),
                    ],
                    result_id="dPWL",
                ),

                # 5) Density correction from B and T
                section_card(
                    "5) Air Density from B & T",
                    ["Density scaling using barometric pressure and temperature (B in mbar, T in K)."],
                    [
                        html.Div(
                            dcc.Markdown(
                                r"$$\rho_2 = \rho_1 \left(\frac{B_2}{B_1}\right)\left(\frac{T_1}{T_2}\right)$$",
                                mathjax=True,
                                style={"textAlign": "center", "width": "100%", "marginBottom": "12px"},
                            ),
                            style={"width": "100%"},
                        ),
                        html.Div([
                            html.Div([html.Label("ρ₁ (kg/m³)"), input_box("rho1_d", 1.20, step=0.01, width="140px")],
                                     style={"display": "flex", "flexDirection": "column"}),
                            html.Div([html.Label("B₁ (mbar)"),  input_box("B1_d", 1013.0, step=1, width="140px")],
                                     style={"display": "flex", "flexDirection": "column"}),
                            html.Div([html.Label("B₂ (mbar)"),  input_box("B2_d", 1013.0, step=1, width="140px")],
                                     style={"display": "flex", "flexDirection": "column"}),
                            html.Div([html.Label("T₁ (K)"),     input_box("T1_d", 293.0, step=0.1, width="140px")],
                                     style={"display": "flex", "flexDirection": "column"}),
                            html.Div([html.Label("T₂ (K)"),     input_box("T2_d", 293.0, step=0.1, width="140px")],
                                     style={"display": "flex", "flexDirection": "column"}),
                        ], style={"display": "flex", "gap": "18px", "flexWrap": "wrap"}),
                    ],
                    result_id="rho2",
                ),

                # 6) Velocity pressure
                section_card(
                    "6) Velocity Pressure",
                    ["Dynamic pressure of air stream (≈ 0.6 V² Pa for standard air, ρ ≈ 1.2 kg/m³)."],
                    [
                        html.Div(
                            dcc.Markdown(
                                r"$$p_d = 0.5\,\rho\,V^2$$",
                                mathjax=True,
                                style={"textAlign": "center", "width": "100%", "marginBottom": "12px"},
                            ),
                            style={"width": "100%"},
                        ),
                        html.Div([
                            html.Div([html.Label("ρ (kg/m³)"),  input_box("rho_vp", 1.20, step=0.01, width="140px")],
                                     style={"display": "flex", "flexDirection": "column"}),
                            html.Div([html.Label("V (m/s)"),    input_box("V_vp", 10.0, step=0.1, width="140px")],
                                     style={"display": "flex", "flexDirection": "column"}),
                        ], style={"display": "flex", "gap": "18px", "flexWrap": "wrap"}),
                    ],
                    result_id="pd_vp",
                ),
            ],
        ),



        html.Div("AWP • Mechanical Handbook", style={"textAlign": "center", "color": "#5f6368", "marginTop": "22px"}),
    ],
)

# -------------------- Callbacks --------------------

@callback(
    Output("q2", "children"),
    Input("q1", "value"),
    Input("n1", "value"),
    Input("n2", "value"),
    Input("d1", "value"),
    Input("d2", "value"),
)
def calc_q2(q1, n1, n2, d1, d2):
    if None in (q1, n1, n2, d1, d2) or float(n1) == 0 or float(d1) == 0:
        return ""
    q2 = float(q1) * (float(n2)/float(n1)) * (float(d2)/float(d1))**3
    return f"q₂ = {q2:,.4f} m³/s"

@callback(
    Output("p2", "children"),
    Input("p1", "value"),
    Input("n1_p", "value"), Input("n2_p", "value"),
    Input("d1_p", "value"), Input("d2_p", "value"),
    Input("rho1_p", "value"), Input("rho2_p", "value"),
)
def calc_p2(p1, n1, n2, d1, d2, rho1, rho2):
    if None in (p1, n1, n2, d1, d2, rho1, rho2) or float(n1) == 0 or float(d1) == 0 or float(rho1) == 0:
        return ""
    p2 = float(p1) * (float(n2)/float(n1))**2 * (float(d2)/float(d1))**2 * (float(rho2)/float(rho1))
    return f"p₂ = {p2:,.2f} Pa"

@callback(
    Output("P2", "children"),
    Input("P1", "value"),
    Input("n1_P", "value"), Input("n2_P", "value"),
    Input("d1_P", "value"), Input("d2_P", "value"),
    Input("rho1_P", "value"), Input("rho2_P", "value"),
)
def calc_P2(P1, n1, n2, d1, d2, rho1, rho2):
    if None in (P1, n1, n2, d1, d2, rho1, rho2) or float(n1) == 0 or float(d1) == 0 or float(rho1) == 0:
        return ""
    P2 = float(P1) * (float(n2)/float(n1))**3 * (float(d2)/float(d1))**5 * (float(rho2)/float(rho1))
    return f"P₂ = {P2:,.3f} kW"

@callback(
    Output("dPWL", "children"),
    Input("d1_spl", "value"), Input("d2_spl", "value"),
    Input("n1_spl", "value"), Input("n2_spl", "value"),
    Input("c1_spl", "value"), Input("c2_spl", "value"),
)
def calc_dPWL(d1, d2, n1, n2, c1, c2):
    if None in (d1, d2, n1, n2, c1, c2) or float(d1) == 0 or float(n1) == 0 or float(c1) == 0:
        return ""
    dPWL = 70*log10(float(d2)/float(d1)) + 55*log10(float(n2)/float(n1)) + 20*log10(float(c2)/float(c1))
    return f"ΔPWL = {dPWL:,.2f} dB"

@callback(
    Output("rho2", "children"),
    Input("rho1_d", "value"),
    Input("B1_d", "value"), Input("B2_d", "value"),
    Input("T1_d", "value"), Input("T2_d", "value"),
)
def calc_rho2(rho1, B1, B2, T1, T2):
    if None in (rho1, B1, B2, T1, T2) or float(B1) == 0 or float(T2) == 0:
        return ""
    rho2 = float(rho1) * (float(B2)/float(B1)) * (float(T1)/float(T2))
    return f"ρ₂ = {rho2:,.4f} kg/m³"

@callback(
    Output("pd_vp", "children"),
    Input("rho_vp", "value"),
    Input("V_vp", "value"),
)
def calc_velocity_pressure(rho, V):
    if None in (rho, V):
        return ""
    pd = 0.5 * float(rho) * (float(V)**2)
    return f"p_d = {pd:,.2f} Pa"
