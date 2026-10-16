from dash import register_page, html, dcc, Input, Output, callback

register_page(__name__, path="/max-pressure", name="Max Pressure")

# -----------------------
# NCC J6D8 tables
# -----------------------
tables = {
    "J6D8a – Non-distributive constant speed": {
        "diameters": ["≤ 20", "25", "32", "40", "50", "65", "80", "100", "125", "≥ 150"],
        "≤5000": [400, 400, 400, 400, 400, 400, 400, 400, 400, 400],
        ">5000": [400, 400, 400, 400, 350, 350, 350, 200, 200, 200],
        "hours_type": ["≤5000", ">5000"],
    },
    "J6D8b – Non-distributive variable speed": {
        "diameters": ["≤ 20", "25", "32", "40", "50", "65", "80", "100", "125", "≥ 150"],
        "≤5000": [400, 400, 400, 400, 400, 400, 400, 400, 400, 400],
        ">5000": [400, 400, 400, 400, 400, 400, 400, 300, 300, 300],
        "hours_type": ["≤5000", ">5000"],
    },
    "J6D8c – Distributive constant speed": {
        "diameters": ["≤ 20", "25", "32", "40", "50", "65", "80", "100", "125", "≥ 150"],
        "≤2000": [400, 400, 400, 400, 400, 400, 400, 400, 400, 400],
        "2000–5000": [300, 220, 220, 220, 220, 400, 400, 400, 400, 400],
        ">5000": [150, 100, 100, 100, 100, 170, 170, 170, 170, 170],
        "hours_type": ["≤2000", "2000–5000", ">5000"],
    },
    "J6D8d – Distributive variable speed": {
        "diameters": ["≤ 20", "25", "32", "40", "50", "65", "80", "100", "125", "≥ 150"],
        "≤5000": [400, 400, 400, 400, 400, 400, 400, 400, 400, 400],
        ">5000": [250, 180, 180, 180, 180, 300, 300, 300, 300, 300],
        "hours_type": ["≤5000", ">5000"],
    },
}

# -----------------------
# Layout
# -----------------------
layout = html.Div(
    style={"width": "100%", "padding": "16px", "fontFamily": "Segoe UI, Inter, Arial"},
    children=[
        html.H2("NCC 2022 — Maximum Pipework Pressure Drop Calculator"),

        html.Label("Select system type:"),
        dcc.Dropdown(
            id="system-type",
            options=[{"label": k, "value": k} for k in tables.keys()],
            value="J6D8a – Non-distributive constant speed",
        ),

        html.Label("Select pipe diameter (mm):", style={"marginTop": "12px"}),
        dcc.Dropdown(id="pipe-diameter"),

        html.Label("Select operating hours range:", style={"marginTop": "12px"}),
        dcc.Dropdown(id="operating-hours"),

        html.Div(
            id="pressure-output",
            style={
                "marginTop": "20px",
                "padding": "16px",
                "borderRadius": "8px",
                "backgroundColor": "#d4edda",  # light green
                "color": "#155724",
                "fontWeight": "600",
                "fontSize": "20px",
                "textAlign": "center",
            },
        ),
    ],
)

# -----------------------
# Callbacks
# -----------------------
@callback(
    Output("pipe-diameter", "options"),
    Output("pipe-diameter", "value"),
    Output("operating-hours", "options"),
    Output("operating-hours", "value"),
    Input("system-type", "value"),
)
def update_dropdowns(system_type):
    table = tables[system_type]

    diameters = table["diameters"]
    diameter_options = [{"label": d, "value": d} for d in diameters]
    diameter_value = diameters[0]

    hours_options = [{"label": h + " hours", "value": h} for h in table["hours_type"]]
    hours_value = table["hours_type"][0]

    return diameter_options, diameter_value, hours_options, hours_value


@callback(
    Output("pressure-output", "children"),
    Input("system-type", "value"),
    Input("pipe-diameter", "value"),
    Input("operating-hours", "value"),
)
def calculate_pressure(system_type, diameter, hours):
    if not diameter or not hours:
        return "Select diameter and operating hours"

    table = tables[system_type]
    idx = table["diameters"].index(diameter)

    pressure = table[hours][idx]

    return html.Span([
        "Maximum allowable pressure drop: ",
        html.B(f"{pressure} Pa/m")
    ])