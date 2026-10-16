# apps/pages/grilledata.py
import dash
from dash import register_page, html, dcc, Input, Output, dash_table, callback

register_page(__name__, path="/grilledata", name="Grille Data")

# =========================================================================
# GRILLES DATA
# =========================================================================
GRILLES = [
    {
        "id": "diffuser",
        "name": "Diffuser — Core Pattern 41",
        "image": "grilles/diff_1.png",
        "notes": [
            "Note: '6.5' for the 450×450 grille at Rating 3.0 appears to be a typo in the source "
            "(likely '650') — verify against the original PDF before relying on it.",
            "Throw measurements are at 1.5 m/s (minimum) and 0.65 m/s (maximum) terminal velocities.",
        ],
        "tables": [
            {"title": "Rating vs Total Pressure (Pa)",
             "columns": ["Rating", "1.5", "2.0", "2.5", "3.0", "3.5"],
             "rows": [["Total Pressure (Pa)", 10, 15, 25, 35, 45]]},

            {"title": "150 x 150 mm — Neck Area 0.0225 m²",
             "columns": ["Rating", "1.5", "2.0", "2.5", "3.0", "3.5"],
             "rows": [
                ["L/S", 35, 45, 55, 65, 80],
                ["NR — dB", None, None, None, None, "<22"],
                ["Min–Max Throw (m)", "0.4–1.0", "0.6–1.2", "0.9–1.6", "1.0–2.3", "1.0–2.7"],
             ]},
            {"title": "225 x 225 mm — Neck Area 0.0506 m²",
             "columns": ["Rating", "1.5", "2.0", "2.5", "3.0", "3.5"],
             "rows": [
                ["L/S", 75, 100, 125, 150, 175],
                ["NR — dB", None, None, "<22", 28, 33],
                ["Min–Max Throw (m)", "0.3–1.4", "0.5–1.5", "1.0–2.0", "1.4–3.2", "1.7–3.5"],
             ]},
            {"title": "300 x 300 mm — Neck Area 0.0900 m²",
             "columns": ["Rating", "1.5", "2.0", "2.5", "3.0", "3.5"],
             "rows": [
                ["L/S", 135, 180, 225, 270, 315],
                ["NR — dB", "<22", 23, 24, 28, 32],
                ["Min–Max Throw (m)", "0.8–2.6", "1.0–2.8", "2.0–4.0", "2.3–4.4", "3.0–4.7"],
             ]},
            {"title": "375 x 375 mm — Neck Area 0.1406 m²",
             "columns": ["Rating", "1.5", "2.0", "2.5", "3.0", "3.5"],
             "rows": [
                ["L/S", 210, 281, 345, 420, 490],
                ["NR — dB", None, "<22", 28, 32, 39],
                ["Min–Max Throw (m)", "1.1–3.2", "1.4–3.6", "1.7–4.6", "2.3–5.1", "3.3–5.4"],
             ]},
            {"title": "450 x 450 mm — Neck Area 0.2025 m²",
             "columns": ["Rating", "1.5", "2.0", "2.5", "3.0", "3.5"],
             "rows": [
                ["L/S", 305, 405, 505, "6.5 (sic — see note)", 710],
                ["NR — dB", 25, 26, 32, 35, 42],
                ["Min–Max Throw (m)", "1.0–3.5", "1.4–4.2", "2.8–5.5", "3.5–6.2", "4.1–6.9"],
             ]},
            {"title": "525 x 525 mm — Neck Area 0.2756 m²",
             "columns": ["Rating", "1.5", "2.0", "2.5", "3.0", "3.5"],
             "rows": [
                ["L/S", 415, 550, 690, 825, 965],
                ["NR — dB", 24, 30, 35, 39, 45],
                ["Min–Max Throw (m)", "1.3–4.8", "1.8–5.8", "2.9–6.5", "3.5–7.7", "4.5–8.4"],
             ]},
            {"title": "600 x 600 mm — Neck Area 0.3600 m²",
             "columns": ["Rating", "1.5", "2.0", "2.5", "3.0", "3.5"],
             "rows": [
                ["L/S", 540, 720, 900, 1080, 1260],
                ["NR — dB", 25, 32, 39, 46, 50],
                ["Min–Max Throw (m)", "1.5–4.9", "2.2–5.9", "3.2–6.6", "3.9–7.9", "5.0–8.6"],
             ]},
        ],
    },
    {
        "id": "ra45",
        "name": "Return Air Grille — Model RA45",
        "image": "grilles/ra45_2.png",
        "notes": [
            "Neck areas (m²) correspond to typical size pairs (mm): "
            "0.090 = 300×300 / 600×150 · 0.135 = 450×300 / 900×150 · 0.180 = 600×300 / 900×200 · "
            "0.225 = 750×300 / 600×375 · 0.270 = 900×300 / 600×450 · 0.360 = 1200×300 / 600×600 · "
            "0.405 = 900×450 / 675×600 · 0.540 = 1200×450 / 900×600 · 0.810 = 900×900 / 1350×600 · "
            "1.000 = 1000×1000 / 2000×500 · 1.500 = 1500×1000 / 1225×1225 · 2.000 = 2000×1000 / 1600×1250.",
        ],
        "tables": [
            {"title": "Neck Velocity (m/s) vs Air Flow (L/S) and Neck Area (m²)",
             "columns": ["L/S", "0.090", "0.135", "0.180", "0.225", "0.270", "0.360",
                         "0.405", "0.540", "0.810", "1.000", "1.500", "2.000"],
             "rows": [
                [50, 0.5, None, None, None, None, None, None, None, None, None, None, None],
                [75, 1.0, 0.5, None, None, None, None, None, None, None, None, None, None],
                [100, None, None, 0.5, None, None, None, None, None, None, None, None, None],
                [125, 2.0, 1.0, None, None, None, None, None, None, None, None, None, None],
                [150, None, None, 1.0, 0.5, None, None, None, None, None, None, None, None],
                [175, None, None, None, None, 0.5, None, None, None, None, None, None, None],
                [200, None, None, None, 1.0, None, None, 0.5, None, None, None, None, None],
                [250, 3.0, 2.0, None, None, 1.0, None, None, None, None, None, None, None],
                [300, 4.0, None, 2.0, None, None, None, None, None, None, None, None, None],
                [350, 4.5, 3.0, None, None, None, 1.0, None, None, None, None, None, None],
                [400, 5.0, None, None, 2.0, None, None, 1.0, None, 0.5, None, None, None],
                [450, None, 3.5, None, None, None, None, None, None, None, None, None, None],
                [500, None, 4.0, 3.0, None, 2.0, None, None, 1.0, None, 0.5, None, None],
                [600, None, 5.0, 4.0, 3.0, None, None, None, None, None, None, None, None],
                [700, None, None, 4.5, 3.5, 3.0, 2.0, None, None, 1.0, None, 0.5, None],
                [800, None, None, 5.0, 4.0, 3.5, 2.5, 2.0, None, None, None, None, None],
                [900, None, None, None, 4.5, 4.0, 3.0, 2.5, None, None, None, None, None],
                [1000, None, None, None, 5.0, 4.5, 3.5, 3.0, 2.0, None, 1.0, None, 0.5],
                [1500, None, None, None, None, 5.5, 4.5, 4.0, 3.0, 2.0, None, 1.0, None],
                [2000, None, None, None, None, None, 5.5, 4.5, 4.0, 3.0, 2.0, 1.5, None],
                [2500, None, None, None, None, None, None, 5.5, 5.0, 3.5, 2.5, 2.0, 1.0],
                [3000, None, None, None, None, None, None, None, None, 4.0, 3.0, 2.5, None],
                [3500, None, None, None, None, None, None, None, None, 5.0, 3.5, 2.75, None],
                [4000, None, None, None, None, None, None, None, None, None, 4.0, 3.0, 2.0],
                [5000, None, None, None, None, None, None, None, None, None, 5.0, 3.5, 3.0],
             ]},
        ],
    },
    {
        "id": "dfc",
        "name": "Relief Air Door Grille — Model DFC",
        "image": "grilles/dfc_3.png",
        "notes": [
            "Neck areas (m²) correspond to typical sizes (mm): "
            "0.045 = 300×150 · 0.068 = 450×150 · 0.090 = 600×150 · 0.120 = 600×200 · 0.135 = 450×300 · "
            "0.150 = 600×250 · 0.180 = 600×300 · 0.203 = 450×450 · 0.270 = 600×450 · 0.360 = 600×600 "
            "(for the neck velocity table below, also 0.540 = 900×600 · 0.720 = 1200×600 · "
            "0.810 = 900×900 · 1.080 = 1200×900 · 1.440 = 1200×1200).",
        ],
        "tables": [
            {"title": "Static Pressure (Pa) vs Air Flow (L/S) and Neck Area (m²)",
             "columns": ["L/S", "0.045", "0.068", "0.090", "0.120", "0.135",
                         "0.150", "0.180", "0.203", "0.270", "0.360"],
             "rows": [
                [30, None, None, None, None, None, None, None, None, None, None],
                [50, 13, None, None, None, None, None, None, None, None, None],
                [75, 35, 15, 9, None, None, None, None, None, None, None],
                [100, 90, 40, 22, 12, 8, 6, None, None, None, None],
                [150, None, 62, 35, 18, 14, 12, 8, 5, None, None],
                [200, None, None, 82, 40, 30, 25, 17, 13, 8, None],
                [250, None, None, None, 75, 55, 45, 30, 24, 13, 8],
                [300, None, None, None, 85, 70, 45, 37, 20, 12, None],
                [400, None, None, None, None, 100, 68, 52, 28, 17, None],
                [500, None, None, None, None, None, None, 90, 50, 30, None],
                [600, None, None, None, None, None, None, None, 80, 45, None],
             ]},
            {"title": "Neck Velocity (m/s) vs Air Flow (L/S) and Neck Area (m²)",
             "columns": ["L/S", "0.045", "0.068", "0.090", "0.120", "0.135", "0.150", "0.180",
                         "0.203", "0.270", "0.360", "0.540", "0.720", "0.810", "1.080", "1.440"],
             "rows": [
                [30, 0.75, 0.5, None, None, None, None, None, None, None, None, None, None, None, None, None],
                [50, 1.5, None, 0.6, 0.5, None, None, None, None, None, None, None, None, None, None, None],
                [75, 2.25, 1.5, 1.0, None, 0.6, 0.5, None, None, None, None, None, None, None, None, None],
                [100, 2.75, 2.0, 1.5, 1.0, None, None, 0.6, 0.5, None, None, None, None, None, None, None],
                [150, 4.0, 2.75, 2.0, 1.5, 1.25, 1.1, 0.9, None, None, None, None, None, None, None, None],
                [200, 5.5, 3.75, 2.75, 2.0, 1.75, 1.5, 1.25, 1.1, 0.5, None, None, None, None, None, None],
                [250, None, 4.5, 3.5, 2.5, 2.0, 1.75, 1.5, 1.4, 1.0, 0.75, 0.5, None, None, None, None],
                [300, None, 5.5, 4.0, 3.0, 2.5, 2.25, 1.9, 1.75, 1.25, None, 0.5, None, None, None, None],
                [400, None, None, 5.0, 4.0, 3.5, 3.0, 2.5, 2.25, 1.75, 1.25, None, None, 0.5, None, None],
                [500, None, None, None, 5.0, 4.0, 3.75, 3.0, 2.75, 2.0, 1.5, 1.0, None, None, 0.5, None],
                [600, None, None, None, 5.0, 4.75, 3.75, 3.25, 2.5, 1.75, None, 0.75, None, None, None, 0.5],
                [750, None, None, None, None, None, 5.0, 4.5, 3.0, 2.5, 1.5, None, None, None, None, None],
                [1000, None, None, None, None, None, None, None, None, 4.0, 3.0, 2.0, 1.5, 1.0, 1.0, None],
                [1500, None, None, None, None, None, None, None, None, None, 4.5, 3.0, 2.25, 2.0, 1.5, 1.0],
                [2000, None, None, None, None, None, None, None, None, None, None, 4.0, 3.0, 3.5, 2.0, None],
                [3000, None, None, None, None, None, None, None, None, None, None, 6.0, 4.5, 4.0, 3.0, 2.0],
                [4000, None, None, None, None, None, None, None, None, None, None, None, 6.0, 5.0, 4.0, 3.0],
             ]},
        ],
    },
    {
        "id": "oal",
        "name": "Weatherproof Louvre — Models OAL-75, OAL-50, OAL-100",
        "image": "grilles/oal_4.png",
        "notes": [
            "Neck areas (m²) correspond to typical size pairs (mm): "
            "0.09 = 300×300 / 600×150 · 0.135 = 450×300 / 675×200 · 0.18 = 600×300 / 450×400 · "
            "0.203 = 450×450 / 675×300 · 0.27 = 600×450 / 900×300 · 0.36 = 600×600 / 900×400 · "
            "0.405 = 900×450 / 675×600 · 0.54 = 900×600 / 1200×450 · 0.72 = 1200×600 / 900×800 · "
            "0.81 = 900×900 / 1350×600 · 1.08 = 1200×900 / 1080×1000 · 1.44 = 1200×1200 / 1600×900.",
        ],
        "tables": [
            {"title": "Neck Velocity (m/s) vs Airflow (L/S) and Neck Area (m²)",
             "columns": ["L/S", "0.09", "0.135", "0.18", "0.203", "0.27", "0.36",
                         "0.405", "0.54", "0.72", "0.81", "1.08", "1.44"],
             "rows": [
                [100, 1.25, 0.75, 0.6, 0.5, None, None, None, None, None, None, None, None],
                [150, 1.75, 1.25, 1.0, 0.75, 0.5, 0.4, None, None, None, None, None, None],
                [200, 2.5, 1.5, 1.25, 1.0, 0.75, 1.25, 0.5, None, None, None, None, None],
                [300, 4, 2.5, 2.0, 1.5, 1.25, 0.8, 0.7, None, None, None, None, None],
                [400, 5, 3, 2.5, 2, 1.5, 1.25, 1.0, 0.75, 0.6, 0.5, None, None],
                [500, None, 4, 3, 2.5, 2, 1.5, 1.25, 1.0, 0.7, 0.6, 0.5, None],
                [600, None, 5, 4, 3.25, 2.5, 1.75, 1.5, 1.25, 0.8, 0.7, 0.75, None],
                [1000, None, None, 6, 5, 4, 3, 2.5, 2.0, 1.5, 1.3, 1.0, None],
                [1500, None, None, None, None, 6, 4.5, 3, 2.75, 2.25, 2.0, 1.5, 0.75],
                [2000, None, None, None, None, None, 6, 5, 4, 3, 2.7, 2.0, 1.5],
                [2500, None, None, None, None, None, None, None, 5, 3.6, 3.4, 2.5, 1.75],
                [3000, None, None, None, None, None, None, None, None, 4.2, 4, 3, 2.25],
                [4000, None, None, None, None, None, None, None, None, 5.2, 5, 4, 3],
                [5000, None, None, None, None, None, None, None, None, None, None, 5, 3.5],
                [6000, None, None, None, None, None, None, None, None, None, None, None, 4],
                [7000, None, None, None, None, None, None, None, None, None, None, None, 5],
                [8000, None, None, None, None, None, None, None, None, None, None, None, None],
                [9000, None, None, None, None, None, None, None, None, None, None, None, None],
             ]},
        ],
    },
]

# =========================================================================
# LAYOUT
# =========================================================================
layout = html.Div(
    style={"width": "100%", "maxWidth": "1000px", "margin": "20px auto",
           "fontFamily": "Segoe UI, Inter, Arial"},
    children=[
        html.H1("Grille Data"),
        html.P("Click a grille's picture to view its performance tables."),

        html.Div(
            style={"display": "flex", "flexWrap": "wrap", "gap": "14px", "marginBottom": "28px"},
            children=[
                html.Button(
                    id={"type": "grille-card", "index": g["id"]},
                    n_clicks=0,
                    style={
                        "border": "1px solid #ddd", "borderRadius": "10px", "padding": "10px",
                        "cursor": "pointer", "background": "#fff", "textAlign": "center",
                        "width": "220px",
                    },
                    children=[
                        html.Img(
                            src=dash.get_asset_url(g["image"]),
                            style={"width": "100%", "height": "140px", "objectFit": "contain"},
                        ),
                        html.Div(g["name"],
                                  style={"marginTop": "8px", "fontSize": "13px", "fontWeight": "600"}),
                    ],
                )
                for g in GRILLES
            ],
        ),

        dcc.Store(id="selected-grille", data=GRILLES[0]["id"]),
        html.Div(id="grille-tables"),
    ],
)

# =========================================================================
# CALLBACKS
# =========================================================================
@callback(
    Output("selected-grille", "data"),
    Input({"type": "grille-card", "index": dash.ALL}, "n_clicks"),
)
def update_selection(n_clicks_list):
    triggered_id = dash.ctx.triggered_id
    if isinstance(triggered_id, dict) and triggered_id.get("type") == "grille-card":
        return triggered_id["index"]
    return GRILLES[0]["id"]


@callback(
    Output("grille-tables", "children"),
    Input("selected-grille", "data"),
)
def show_tables(grille_id):
    grille = next((g for g in GRILLES if g["id"] == grille_id), None)
    if grille is None:
        return html.Div("Grille not found.")

    children = [html.H2(grille["name"])]

    for note in grille.get("notes", []):
        children.append(html.P(note, style={"fontStyle": "italic", "color": "#444", "marginBottom": "4px"}))

    for table in grille["tables"]:
        children.append(html.H4(table["title"], style={"marginTop": "16px", "marginBottom": "6px"}))
        children.append(
            dash_table.DataTable(
                columns=[{"name": str(c), "id": str(c)} for c in table["columns"]],
                data=[dict(zip([str(c) for c in table["columns"]], row)) for row in table["rows"]],
                style_cell={"textAlign": "center", "padding": "8px", "fontSize": "13px"},
                style_header={"fontWeight": "600", "backgroundColor": "#f2f2f2"},
                style_table={"marginBottom": "26px", "maxWidth": "950px", "overflowX": "auto"},
            )
        )

    return children