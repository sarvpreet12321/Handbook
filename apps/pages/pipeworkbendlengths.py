# apps/pages/pipeworkbendlengths.py
import dash
from dash import register_page, html, dcc, Input, Output, dash_table, callback

register_page(__name__, path="/pipeworkbendlengths", name="Pipework Bend Equivalent Lengths")

# =========================================================================
# DATA
# All fittings share the same columns: Nominal diameter of pipe (mm).
# Some images (e.g. gate_valve) cover several rows of the original table,
# since one diagram represents several positions/ratios of the same fitting.
# =========================================================================
COLUMNS = ["Fitting", "32", "40", "50", "65", "80", "100", "125", "150", "200"]

FITTINGS = [
    {
        "id": "45_degree_elbow", "name": "45° Elbow",
        "image": "bend_fittings/45_degree_elbow.png",
        "rows": [["45° Elbow", 0.52, 0.64, 0.77, 0.93, 1.2, 1.55, 1.85, 2.15, 2.9]],
    },
    {
        "id": "angle_valve_open", "name": "Angle Valve Open",
        "image": "bend_fittings/angle_valve_open.png",
        "rows": [["Angle Valve Open", 6, 7.2, 8.6, 10, 13.5, 17.5, 22, 26, 34]],
    },
    {
        "id": "borda_entrance", "name": "Borda Entrance",
        "image": "bend_fittings/borda_entrance.png",
        "rows": [["Borda Entrance", 1.2, 1.3, 1.6, 1.8, 2.4, 3.1, 4, 4.6, 6]],
    },
    {
        "id": "close_return_bend", "name": "Close Return Bend",
        "image": "bend_fittings/close_return_bend.png",
        "rows": [["Close Return Bend", 2.6, 3.1, 3.8, 4.5, 5.8, 7.6, 9.1, 11, 15]],
    },
    {
        "id": "gate_valve", "name": "Gate Valve",
        "image": "bend_fittings/gate_valve.png",
        "rows": [
            ["Gate Valve 3/4 Closed", 33, 37, 46, 55, 73, 95, 120, 140, 165],
            ["Gate Valve 1/2 Closed", 7.6, 8.9, 11, 13, 17, 22, 28, 32, 42],
            ["Gate Valve 1/4 Closed", 1.5, 1.7, 2.1, 2.5, 3.2, 4.3, 5.4, 6.1, 8],
            ["Gate Valve Fully Open", 0.26, 0.32, 0.38, 0.43, 0.52, 0.69, 0.9, 1.1, 1.3],
        ],
    },
    {
        "id": "globe_valve_open", "name": "Globe Valve Open",
        "image": "bend_fittings/globe_valve_open.png",
        "rows": [["Globe Valve Open", 12, 14, 17, 20, 26, 35, 42, 51, 67]],
    },
    {
        "id": "long_sweep_elbow_or_run_of_standard_tee", "name": "Long Sweep Elbow or Run of Standard Tee",
        "image": "bend_fittings/long_sweep_elbow_or_run_of_standard_tee.png",
        "rows": [["Long Sweep Elbow or Run of Standard Tee", 0.72, 0.9, 1.15, 1.3, 1.65, 2.1, 2.6, 3.1, 4.1]],
    },
    {
        "id": "medium_sweep_elbow_or_run_of_tee_reduced_quarter", "name": "Medium Sweep Elbow or Run of Tee Reduced 1/4",
        "image": "bend_fittings/medium_sweep_elbow_or_run_of_tee_reduced_quarter.png",
        "rows": [["Medium Sweep Elbow or Run of Tee Reduced 1/4", 1, 1.2, 1.4, 1.65, 2.1, 2.75, 3.45, 4.1, 5.5]],
    },
    {
        "id": "ordinary_entrance", "name": "Ordinary Entrance",
        "image": "bend_fittings/ordinary_entrance.png",
        "rows": [["Ordinary Entrance", 0.63, 0.66, 0.95, 1.15, 1.4, 1.8, 2.25, 2.65, 3.45]],
    },
    {
        "id": "square_elbow", "name": "Square Elbow",
        "image": "bend_fittings/square_elbow.png",
        "rows": [["Square Elbow", 2.3, 2.8, 3.4, 4.1, 5.3, 6.9, 8.1, 9.8, 13]],
    },
    {
        "id": "standard_elbow_or_run_of_tee_reduced_half", "name": "Standard Elbow or Run of Tee Reduced 1/2",
        "image": "bend_fittings/standard_elbow_or_run_of_tee_reduced_half.png",
        "rows": [["Standard Elbow or Run of Tee Reduced 1/2", 1.3, 1.4, 1.7, 1.9, 2.6, 3.4, 4.2, 5, 6.2]],
    },
    {
        "id": "standard_tee", "name": "Standard Tee",
        "image": "bend_fittings/standard_tee.png",
        "rows": [["Standard Tee", 2.3, 2.8, 3.4, 4.1, 5.3, 6.9, 8.1, 9.8, 13]],
    },
    {
        "id": "standard_tee_through_side_outlet", "name": "Standard Tee Through Side Outlet",
        "image": "bend_fittings/standard_tee_through_side_outlet.png",
        "rows": [["Standard Tee Through Side Outlet", 2.3, 2.8, 3.4, 4.1, 5.3, 6.9, 8.1, 9.8, 13]],
    },
    {
        "id": "sudden_contraction", "name": "Sudden Contraction",
        "image": "bend_fittings/sudden_contraction.png",
        "rows": [
            ["Sudden Contraction d/D 1/4", 0.52, 0.64, 0.77, 0.93, 1.2, 1.55, 1.85, 2.15, 2.9],
            ["Sudden Contraction d/D 1/2", 0.42, 0.49, 0.59, 0.68, 0.88, 1.2, 1.5, 1.65, 2.2],
            ["Sudden Contraction d/D 3/4", 0.26, 0.32, 0.38, 0.43, 0.52, 0.69, 0.9, 1.1, 1.3],
        ],
    },
    {
        "id": "sudden_entrance", "name": "Sudden Entrance",
        "image": "bend_fittings/sudden_entrance.png",
        "rows": [
            ["Sudden Entrance d/D 1/4", 1.3, 1.4, 1.7, 1.9, 2.6, 3.4, 4.2, 5, 6.2],
            ["Sudden Entrance d/D 1/2", 0.68, 0.83, 1.05, 1.25, 1.6, 1.9, 2.5, 2.9, 3.9],
            ["Sudden Entrance d/D 3/4", 0.63, 0.66, 0.95, 1.15, 1.4, 1.8, 2.25, 2.65, 3.45],
        ],
    },
    {
        "id": "swing_check_valve_fully_open", "name": "Swing Check Valve Open",
        "image": "bend_fittings/swing_check_valve_fully_open.png",
        "rows": [["Swing Check Valve Open", 3, 3.5, 4.4, 5.2, 6.6, 8.6, 11, 13, 16]],
    },
]

# =========================================================================
# LAYOUT
# =========================================================================
layout = html.Div(
    style={"width": "100%", "maxWidth": "1000px", "margin": "20px auto",
           "fontFamily": "Segoe UI, Inter, Arial"},
    children=[
        html.H1("Pipework Bend Equivalent Lengths"),
        html.P("Click a fitting's picture to view its equivalent length (m) by nominal pipe diameter (mm)."),

        html.Div(
            style={"display": "flex", "flexWrap": "wrap", "gap": "14px", "marginBottom": "28px"},
            children=[
                html.Button(
                    id={"type": "bend-card", "index": f["id"]},
                    n_clicks=0,
                    style={
                        "border": "1px solid #ddd", "borderRadius": "10px", "padding": "10px",
                        "cursor": "pointer", "background": "#fff", "textAlign": "center",
                        "width": "180px",
                    },
                    children=[
                        html.Img(
                            src=dash.get_asset_url(f["image"]),
                            style={"width": "100%", "height": "110px", "objectFit": "contain"},
                        ),
                        html.Div(f["name"],
                                  style={"marginTop": "8px", "fontSize": "12px", "fontWeight": "600"}),
                    ],
                )
                for f in FITTINGS
            ],
        ),

        dcc.Store(id="selected-bend", data=FITTINGS[0]["id"]),
        html.Div(id="bend-table"),
    ],
)

# =========================================================================
# CALLBACKS
# =========================================================================
@callback(
    Output("selected-bend", "data"),
    Input({"type": "bend-card", "index": dash.ALL}, "n_clicks"),
)
def update_selection(n_clicks_list):
    triggered_id = dash.ctx.triggered_id
    if isinstance(triggered_id, dict) and triggered_id.get("type") == "bend-card":
        return triggered_id["index"]
    return FITTINGS[0]["id"]


@callback(
    Output("bend-table", "children"),
    Input("selected-bend", "data"),
)
def show_table(fitting_id):
    fitting = next((f for f in FITTINGS if f["id"] == fitting_id), None)
    if fitting is None:
        return html.Div("Fitting not found.")

    return [
        html.H2(fitting["name"]),
        html.P("Equivalent Length (m) — Nominal Ø mm of Pipe", style={"fontWeight": "600", "marginBottom": "6px"}),
        dash_table.DataTable(
            columns=[{"name": c, "id": c} for c in COLUMNS],
            data=[dict(zip(COLUMNS, row)) for row in fitting["rows"]],
            style_cell={"textAlign": "center", "padding": "8px", "fontSize": "13px"},
            style_cell_conditional=[{"if": {"column_id": "Fitting"}, "textAlign": "left", "minWidth": "260px"}],
            style_header={"fontWeight": "600", "backgroundColor": "#f2f2f2"},
            style_table={"marginBottom": "26px", "maxWidth": "950px", "overflowX": "auto"},
        ),
    ]