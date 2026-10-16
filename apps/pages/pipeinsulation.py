# apps/pages/pipeinsulation.py
import dash
from dash import register_page, html, dcc, Input, Output, dash_table, callback

register_page(__name__, path="/pipeinsulation", name="Pipe Insulation R-Values")

HEAD = "#FFC000"
SECTION = "#D9D9D9"

# =========================================================================
# 6.1 — Application Material R-Value required by BCA/NCC
# =========================================================================
ZONE_COLS = ["1", "2", "3", "4", "5", "6", "7", "8"]

CATEGORIES_61 = [
    {"title": "Heating water piping for systems of not more than 65kW heating capacity", "rows": [
        ("Located Internally", ["R1.0"] * 7 + ["R1.3"]),
        ("Enclosed wall space, sub-floor or roof space", ["R1.1"] * 7 + ["R1.4"]),
        ("Outside or unenclosed sub-floor or roof space", ["R1.2"] * 7 + ["R1.5"]),
    ]},
    {"title": "Heating water piping for systems of more than 65kW heating capacity", "rows": [
        ("Located Internally", ["R1.0"] * 7 + ["R1.7"]),
        ("Enclosed wall space, sub-floor or roof space", ["R1.1"] * 7 + ["R1.8"]),
        ("Outside or unenclosed sub-floor or roof space", ["R1.2", "R1.2", "R1.2", "R1.5", "R1.2", "R1.5", "R1.5", "R1.9"]),
    ]},
    {"title": "Cooling water piping for systems of not more than 65kWr capacity", "rows": [
        ("Located Internally", ["R1.0", "R1.0", "R1.0", "R0.6", "R1.0", "R0.6", "R0.6", "R0.6"]),
        ("Enclosed wall space, sub-floor or roof space", ["R1.1", "R1.1", "R1.1", "R0.7", "R1.1", "R0.7", "R0.7", "R0.7"]),
        ("Outside or unenclosed sub-floor or roof space", ["R1.2", "R1.2", "R1.2", "R0.8", "R1.2", "R0.8", "R0.8", "R0.8"]),
    ]},
    {"title": "Cooling water piping for systems of more than 65kWr capacity but not more than 250kW capacity", "rows": [
        ("Located Internally", ["R1.7", "R1.7", "R1.7", "R1.3", "R1.7", "R1.3", "R1.3", "R1.0"]),
        ("Enclosed wall space, sub-floor or roof space", ["R1.8", "R1.8", "R1.8", "R1.4", "R1.8", "R1.4", "R1.4", "R1.1"]),
        ("Outside or unenclosed sub-floor or roof space", ["R1.9", "R1.9", "R1.9", "R1.5", "R1.9", "R1.5", "R1.5", "R1.2"]),
    ]},
    {"title": "Cooling water piping for systems of more than 250kW capacity", "rows": [
        ("Located Internally", ["R2.0", "R2.0", "R2.0", "R1.7", "R2.0", "R1.7", "R1.7", "R1.3"]),
        ("Enclosed wall space, sub-floor or roof space", ["R2.1", "R2.1", "R2.1", "R1.8", "R2.1", "R1.8", "R1.8", "R1.4"]),
        ("Outside or unenclosed sub-floor or roof space", ["R2.2", "R2.2", "R2.2", "R1.9", "R2.2", "R1.9", "R1.9", "R1.5"]),
    ]},
    {"title": "Refrigerant not more than 20°C — Pipe nominal diameter", "rows": [
        ("15mm – 40mm", ["R1.3"] * 8),
        ("50mm – 80mm", ["R1.7"] * 8),
        ("100mm – 125mm", ["R2.0"] * 8),
        ("150mm", ["R2.0"] * 8),
        ("200mm", ["R2.7"] * 8),
    ]},
    {"title": "Refrigerant more than 20°C but not more than 200°C (see Cooling Water tables above)", "rows": []},
    {"title": "Steam and condensate not more than 120°C — Pipe nominal diameter", "rows": [
        ("15mm – 40mm", ["R1.0"] * 8),
        ("50mm – 80mm", ["R1.0"] * 8),
        ("100mm – 125mm", ["R1.3"] * 8),
        ("150mm", ["R1.3"] * 8),
        ("200mm", ["R1.3"] * 8),
    ]},
    {"title": "Steam more than 120°C — Pipe nominal diameter", "rows": [
        ("15mm – 40mm", ["R1.5"] * 8),
        ("50mm – 80mm", ["R1.5"] * 8),
        ("100mm – 125mm", ["R1.5"] * 8),
        ("150mm", ["R1.8"] * 8),
        ("200mm", ["R2.1"] * 8),
    ]},
]


def application_rvalue_table():
    header = html.Thead([
        html.Tr([
            html.Th("Location", style={"background": HEAD, "border": "1px solid #bbb", "padding": "6px 8px"}),
            html.Th("Climate Zone", colSpan=8, style={"background": HEAD, "border": "1px solid #bbb", "padding": "6px 8px", "textAlign": "center"}),
        ]),
        html.Tr([html.Th("", style={"background": HEAD, "border": "1px solid #bbb", "padding": "6px 8px"})] +
                [html.Th(z, style={"background": HEAD, "border": "1px solid #bbb", "padding": "6px 8px", "textAlign": "center"}) for z in ZONE_COLS]),
    ])

    body_rows = []
    for cat in CATEGORIES_61:
        body_rows.append(html.Tr([html.Td(cat["title"], colSpan=9, style={
            "background": SECTION, "border": "1px solid #bbb", "padding": "6px 8px", "fontWeight": 700,
        })]))
        for label, values in cat["rows"]:
            body_rows.append(html.Tr(
                [html.Td(label, style={"border": "1px solid #ccc", "padding": "6px 8px"})] +
                [html.Td(v, style={"border": "1px solid #ccc", "padding": "6px 8px", "textAlign": "center"}) for v in values]
            ))

    return html.Table(
        style={"borderCollapse": "collapse", "width": "100%", "maxWidth": "1100px"},
        children=[header, html.Tbody(body_rows)],
    )


# =========================================================================
# 6.2 — Recommended Minimum Insulation Material R-Value — Pipework
# =========================================================================
PIPE_COLUMNS = ["Steel Pipe NB", "Copper Pipe NB", "OD (mm)",
                "0.6", "0.7", "0.8", "1.0", "1.1", "1.2", "1.3", "1.4",
                "1.5", "1.7", "1.8", "1.9", "2.0", "2.1", "2.2", "2.7"]

GLASSWOOL_ROWS = [
    ["", 15, 12.7, 25, 25, 25, 25, 25, 25, 25, 25, 25, 38, 38, 38, 38, 38, 38, 50],
    ["", 18, 15.9, 25, 25, 25, 25, 25, 25, 25, 25, 38, 38, 38, 38, 38, 38, 38, 50],
    ["", 20, 19.1, 25, 25, 25, 25, 25, 25, 25, 38, 38, 38, 38, 38, 38, 38, 38, 50],
    ["", 25, 25.4, 25, 25, 25, 25, 25, 25, 38, 38, 38, 38, 38, 38, 38, 50, 50, 50],
    ["", 32, 31.8, 25, 25, 25, 25, 25, 38, 38, 38, 38, 38, 38, 38, 50, 50, 50, 50],
    ["", 40, 38.1, 25, 25, 25, 25, 38, 38, 38, 38, 38, 38, 50, 50, 50, 50, 50, 50],
    ["", 45, 44.5, 25, 25, 25, 25, 38, 38, 38, 38, 38, 38, 50, 50, 50, 50, 50, 63],
    ["", 50, 50.8, 25, 25, 25, 25, 38, 38, 38, 38, 38, 50, 50, 50, 50, 50, 50, 63],
    [50, "", 60.3, 25, 25, 25, 25, 38, 38, 38, 38, 50, 50, 50, 50, 50, 50, 50, 63],
    ["", 65, 63.5, 25, 25, 25, 25, 38, 38, 38, 38, 38, 50, 50, 50, 50, 50, 50, 63],
    ["", 80, 76.1, 25, 25, 25, 38, 38, 38, 38, 38, 38, 50, 50, 50, 50, 50, 50, 63],
    ["", 90, 88.9, 25, 25, 25, 38, 38, 38, 38, 38, 38, 50, 50, 50, 50, 50, 63, 63],
    ["", 100, 101.6, 25, 25, 25, 38, 38, 38, 38, 38, 38, 50, 50, 50, 50, 63, 63, 63],
    [100, "", 114.3, 25, 25, 25, 38, 38, 38, 38, 38, 50, 50, 50, 50, 50, 63, 63, 63],
    ["", 125, 127.0, 25, 25, 25, 38, 38, 38, 38, 38, 50, 50, 50, 50, 50, 63, 63, 75],
    ["", 150, 152.4, 25, 25, 25, 38, 38, 38, 38, 50, 50, 50, 50, 63, 63, 63, 63, 75],
    [150, "", 168.3, 25, 25, 25, 38, 38, 38, 50, 50, 50, 50, 63, 63, 63, 63, 63, 75],
    ["", 175, 177.8, 25, 25, 25, 38, 38, 38, 50, 50, 50, 50, 63, 63, 63, 63, 63, 75],
    ["", 200, 203.2, 25, 25, 25, 38, 38, 38, 50, 50, 50, 50, 63, 63, 63, 63, 63, 75],
    [200, "", 219.1, 25, 25, 25, 38, 38, 38, 50, 50, 50, 50, 63, 63, 63, 63, 63, 75],
    ["", 225, 228.6, 25, 25, 25, 38, 38, 38, 50, 50, 50, 50, 63, 63, 63, 63, 75, 75],
]

ARMAFLEX_ROWS = [
    ["", 15, 12.7, 19, 19, 19, 25, 25, 25, 25, 32, 32, 32, 32, 32, 38, 38, 38, 44],
    ["", 18, 15.9, 19, 19, 19, 25, 25, 25, 25, 32, 32, 32, 38, 38, 38, 38, 38, 44],
    ["", 20, 19.1, 19, 19, 19, 25, 25, 25, 32, 32, 32, 38, 38, 38, 38, 38, 44, 50],
    ["", 25, 25.4, 19, 19, 19, 25, 25, 32, 32, 32, 32, 38, 38, 38, 44, 44, 44, 50],
    ["", 32, 31.8, 19, 19, 25, 25, 32, 32, 32, 32, 38, 38, 38, 44, 44, 44, 44, 63],
    ["", 40, 38.1, 19, 19, 25, 25, 32, 32, 32, 38, 38, 38, 44, 44, 44, 50, 50, 63],
    ["", 45, 44.5, 19, 19, 25, 32, 32, 32, 32, 38, 38, 44, 44, 44, 44, 50, 50, 63],
    ["", 50, 50.8, 19, 25, 25, 32, 32, 32, 38, 38, 38, 44, 44, 44, 50, 50, 50, 63],
    [50, "", 60.3, 19, 25, 25, 32, 32, 32, 38, 38, 44, 44, 44, 50, 50, 50, 63, 63],
    ["", 65, 63.5, 19, 25, 25, 32, 32, 32, 38, 38, 38, 44, 44, 50, 50, 50, 63, 63],
    ["", 80, 76.1, 19, 25, 25, 32, 38, 38, 38, 44, 44, 50, 50, 50, 63, 63, 63, 75],
    ["", 90, 88.9, 19, 25, 25, 32, 38, 38, 38, 44, 50, 50, 50, 63, 63, 63, 63, 75],
    ["", 100, 101.6, 19, 25, 32, 32, 38, 38, 44, 44, 50, 50, 50, 63, 63, 63, 63, 75],
    [100, "", 114.3, 19, 25, 32, 32, 32, 38, 44, 44, 50, 50, 63, 63, 63, 63, 63, 75],
    ["", 125, 127.0, 25, 25, 32, 32, 38, 44, 44, 44, 50, 63, 63, 63, 63, 63, 75, 75],
    ["", 150, 152.4, 25, 25, 32, 32, 38, 44, 44, 44, 50, 63, 63, 63, 63, 63, 75, 75],
    [150, "", 168.3, 25, 25, 32, 32, 38, 38, 44, 44, 50, 63, 63, 63, 63, 63, 75, 75],
    ["", 175, 177.8, 25, 25, 32, 32, 38, 38, 44, 44, 50, 50, 63, 63, 63, 63, 63, 75],
    ["", 200, 203.2, 25, 25, 32, 32, 38, 38, 44, 44, 50, 63, 63, 63, 63, 63, 63, 75],
    [200, "", 219.1, 25, 25, 32, 32, 38, 38, 44, 44, 50, 63, 63, 63, 63, 63, 75, 84],
    ["", 225, 228.6, 25, 25, 32, 32, 38, 38, 44, 44, 50, 63, 63, 63, 63, 63, 75, 84],
]

POLYSTYRENE_ROWS = [
    ["", 15, 12.7, 25, 25, 25, 25, 25, 25, 38, 38, 38, 38, 38, 38, 38, 38, 50, 50],
    ["", 18, 15.9, 25, 25, 25, 25, 25, 38, 38, 38, 38, 38, 38, 50, 50, 50, 50, 63],
    ["", 20, 19.1, 25, 25, 25, 25, 38, 38, 38, 38, 38, 38, 50, 50, 50, 50, 63, 63],
    ["", 25, 25.4, 25, 25, 25, 25, 38, 38, 38, 38, 38, 50, 50, 50, 50, 50, 63, 63],
    ["", 32, 31.8, 25, 25, 25, 38, 38, 38, 38, 38, 50, 50, 50, 50, 50, 63, 63, 63],
    ["", 40, 38.1, 25, 25, 25, 38, 38, 38, 38, 38, 50, 50, 50, 50, 50, 63, 63, 63],
    ["", 45, 44.5, 25, 25, 25, 38, 38, 38, 38, 50, 50, 50, 50, 50, 63, 63, 63, 63],
    ["", 50, 50.8, 25, 25, 25, 38, 38, 38, 38, 50, 50, 50, 50, 63, 63, 63, 63, 63],
    [50, "", 60.3, 25, 25, 25, 38, 38, 38, 50, 50, 50, 50, 63, 63, 63, 63, 63, 75],
    ["", 65, 63.5, 25, 25, 25, 38, 38, 38, 50, 50, 50, 63, 63, 63, 63, 63, 63, 75],
    ["", 80, 76.1, 25, 25, 38, 38, 38, 50, 50, 50, 50, 63, 63, 63, 63, 63, 63, 75],
    ["", 90, 88.9, 25, 25, 38, 38, 38, 50, 50, 50, 63, 63, 63, 63, 63, 63, 75, 75],
    ["", 100, 101.6, 25, 25, 38, 38, 38, 50, 50, 50, 63, 63, 63, 63, 63, 63, 75, 75],
    [100, "", 114.3, 25, 25, 38, 38, 50, 50, 50, 50, 63, 63, 63, 63, 63, 75, 75, 75],
    ["", 125, 127.0, 25, 25, 38, 38, 50, 50, 50, 50, 63, 63, 63, 63, 75, 75, 75, 100],
    ["", 150, 152.4, 25, 25, 38, 38, 50, 50, 50, 63, 63, 63, 63, 75, 75, 75, 75, 100],
    [150, "", 168.3, 25, 38, 38, 38, 50, 50, 50, 63, 63, 63, 63, 75, 75, 75, 75, 100],
    ["", 175, 177.8, 25, 38, 38, 38, 50, 50, 50, 63, 63, 63, 75, 75, 75, 75, 100, 100],
    ["", 200, 203.2, 25, 38, 38, 50, 50, 50, 63, 63, 63, 63, 75, 75, 75, 75, 100, 100],
    [200, "", 219.1, 25, 38, 38, 50, 50, 50, 63, 63, 63, 63, 75, 75, 75, 100, 100, 100],
    ["", 225, 228.6, 25, 38, 38, 50, 50, 50, 63, 63, 63, 63, 75, 75, 75, 100, 100, 100],
]

MATERIALS = [
    {"id": "glasswool", "name": "Glasswool — Preformed", "rows": GLASSWOOL_ROWS},
    {"id": "armaflex", "name": "FR (Fire Retardant) Armaflex — Preformed", "rows": ARMAFLEX_ROWS},
    {"id": "polystyrene", "name": "Polystyrene SL Grade", "rows": POLYSTYRENE_ROWS},
]

# =========================================================================
# LAYOUT
# =========================================================================
layout = html.Div(
    style={"width": "100%", "maxWidth": "1100px", "margin": "20px auto", "fontFamily": "Segoe UI, Inter, Arial"},
    children=[
        html.H1("Pipe Insulation R-Values"),
        html.P("The BCA/NCC also covers pipe insulation energy efficiency, which in part requires the "
               "following material R-Values."),

        html.H2("6.1 Application Material R-Value Required by BCA/NCC"),
        html.P("Read off the required R-Value from the table below, then choose the appropriate product "
               "using the material selector further down this page."),
        application_rvalue_table(),
        html.P(
            "Note: Piping to be insulated includes all flow and return piping, cold water supply piping "
            "within 500mm of the connection to the heating and cooling system and pressure relief piping "
            "within 500mm of the connection to the heating and cooling system. Tanks, vessels and heat "
            "exchangers must comply to BCA Vol 1 Spec. J5.4 — R-Values range from R1.3 – R2.5.",
            style={"fontStyle": "italic", "fontSize": "13px", "marginTop": "10px"},
        ),

        html.Hr(style={"margin": "32px 0"}),

        html.H2("6.2 Recommended Minimum Insulation Material R-Value — Pipework"),
        html.P("Select which insulation material best suits your application, then read across from the "
               "pipe size to determine the required insulation thickness (mm) to meet the R-Value for "
               "your application. The R_MAT values are calculated based on the preformed sectional pipe "
               "method calculation of AS4859.1."),

        html.Div(
            style={"display": "flex", "gap": "12px", "marginBottom": "20px", "flexWrap": "wrap"},
            children=[
                html.Button(
                    m["name"],
                    id={"type": "material-btn", "index": m["id"]},
                    n_clicks=0,
                    style={
                        "padding": "10px 18px", "borderRadius": "8px", "border": "1px solid #ccc",
                        "background": "#fff", "cursor": "pointer", "fontWeight": 600, "fontSize": "14px",
                    },
                )
                for m in MATERIALS
            ],
        ),

        dcc.Store(id="selected-material", data="glasswool"),
        html.Div(id="material-table"),
    ],
)

# =========================================================================
# CALLBACKS
# =========================================================================
@callback(
    Output("selected-material", "data"),
    Input({"type": "material-btn", "index": dash.ALL}, "n_clicks"),
)
def update_material(n_clicks_list):
    triggered_id = dash.ctx.triggered_id
    if isinstance(triggered_id, dict) and triggered_id.get("type") == "material-btn":
        return triggered_id["index"]
    return "glasswool"


@callback(
    Output("material-table", "children"),
    Input("selected-material", "data"),
)
def show_material_table(material_id):
    material = next((m for m in MATERIALS if m["id"] == material_id), None)
    if material is None:
        return html.Div("Material not found.")

    return [
        html.H3(material["name"]),
        dash_table.DataTable(
            columns=[{"name": c, "id": c} for c in PIPE_COLUMNS],
            data=[dict(zip(PIPE_COLUMNS, row)) for row in material["rows"]],
            style_cell={"textAlign": "center", "padding": "6px", "fontSize": "12px"},
            style_header={"fontWeight": "600", "backgroundColor": HEAD, "fontSize": "12px"},
            style_table={"overflowX": "auto", "maxWidth": "1100px"},
        ),
    ]