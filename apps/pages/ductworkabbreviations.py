# apps/pages/ductwork_abbreviations.py
from dash import register_page, html, dcc, dash_table, Input, Output, callback
from apps.shared.ui import BRAND, MUTED, BLACK  # remove if not in your project

register_page(__name__, path="/ductworkabbreviations", name="Ductwork Abbreviations")

# ---------------- Data ----------------
ROWS = [
    # Ductwork
    {"Category": "Ductwork", "Abbrev": "S.M.",   "Meaning": "Site Measure"},
    {"Category": "Ductwork", "Abbrev": "EXP",    "Meaning": "Exposed Duct"},
    {"Category": "Ductwork", "Abbrev": "T.C.",   "Meaning": "To Cut on Site"},
    {"Category": "Ductwork", "Abbrev": "E.T.",   "Meaning": "Equal Taper"},
    {"Category": "Ductwork", "Abbrev": "F.O.T.", "Meaning": "Flat on Top"},
    {"Category": "Ductwork", "Abbrev": "F.O.B.", "Meaning": "Flat on Bottom"},
    {"Category": "Ductwork", "Abbrev": "S.E.",   "Meaning": "Stop End"},
    {"Category": "Ductwork", "Abbrev": "S.U. ▶",   "Meaning": "Set Up in Direction of Arrow"},
    {"Category": "Ductwork", "Abbrev": "S.D. ▶",   "Meaning": "Set Down in Direction of Arrow"},
    {"Category": "Ductwork", "Abbrev": "D.M.",   "Meaning": "Duct Mate"},
    {"Category": "Ductwork", "Abbrev": "S.J.",   "Meaning": "Slide Joint"},
    {"Category": "Ductwork", "Abbrev": "FL",     "Meaning": "Flange"},
    {"Category": "Ductwork", "Abbrev": "L",      "Meaning": "Long"},

    # Air Systems
    {"Category": "Air Systems", "Abbrev": "S/A",    "Meaning": "Supply Air"},
    {"Category": "Air Systems", "Abbrev": "R/A",    "Meaning": "Return Air"},
    {"Category": "Air Systems", "Abbrev": "O/A",    "Meaning": "Outside Air"},
    {"Category": "Air Systems", "Abbrev": "E/A",    "Meaning": "Exhaust Air"},
    {"Category": "Air Systems", "Abbrev": "REL/A",  "Meaning": "Relief Air"},
    {"Category": "Air Systems", "Abbrev": "S.S.",   "Meaning": "Smoke Spill"},

    # System Dampers
    {"Category": "System Dampers", "Abbrev": "V.C.D.",   "Meaning": "Volume Control Damper"},
    {"Category": "System Dampers", "Abbrev": "M.V.C.D.", "Meaning": "Motorised Volume Control Damper"},
    {"Category": "System Dampers", "Abbrev": "O.B.D.",   "Meaning": "Opposed Blade Damper"},
    {"Category": "System Dampers", "Abbrev": "B.D.",     "Meaning": "Butterfly Damper"},
    {"Category": "System Dampers", "Abbrev": "N.R.D.",   "Meaning": "Non Return Damper"},
    {"Category": "System Dampers", "Abbrev": "S.S.D.",   "Meaning": "Stream Splitter Damper"},
    {"Category": "System Dampers", "Abbrev": "F.D.",     "Meaning": "Fire Damper"},

    # Other Components
    {"Category": "System Components", "Abbrev": "A.P.",  "Meaning": "Access Panel"},
    {"Category": "System Components", "Abbrev": "A.D.",  "Meaning": "Access Door"},
    {"Category": "System Components", "Abbrev": "D.G.",  "Meaning": "Door Grille"},
    {"Category": "System Components", "Abbrev": "A.H.U.","Meaning": "Air Handling Unit"},
    {"Category": "System Components", "Abbrev": "F.C.U.","Meaning": "Fan Coil Unit"},
    {"Category": "System Components", "Abbrev": "E.D.H.","Meaning": "Electrical Duct Heater"},
    {"Category": "System Components", "Abbrev": "Ⓣ",     "Meaning": "Temperature Sensor"},
    {"Category": "System Components", "Abbrev": "Ⓗ",     "Meaning": "Humidity Sensor"},
]

COLUMNS = [
    {"name": "Category", "id": "Category"},
    {"name": "Abbrev",   "id": "Abbrev"},
    {"name": "Meaning",  "id": "Meaning"},
]

# ---------------- Layout ----------------
layout = html.Div(
    style={"width": "100%", "padding": "16px", "fontFamily": "Segoe UI, Inter, Arial", "color": BLACK},
    children=[
        # Page header
        html.Div(
            style={"display": "flex", "alignItems": "center", "gap": "14px", "marginBottom": "10px"},
            children=[
                html.Div(style={"width": "12px", "height": "28px", "backgroundColor": BRAND, "borderRadius": "6px"}),
                html.H2("Ductwork Abbreviations", style={"margin": 0}),
            ],
        ),
        html.P("Common abbreviations used in ductwork, air systems, dampers, and components.",
               style={"color": MUTED, "marginTop": 0, "marginBottom": "10px"}),

        # Search
        html.Div([
            html.Label("Search", htmlFor="abbr-search", style={"marginRight": "10px"}),
            dcc.Input(
                id="abbr-search",
                type="text",
                placeholder="e.g. VCD, supply, panel",
                debounce=True,
                style={"width": "300px", "marginRight": "14px"}
            ),
            html.Span(id="abbr-count", style={"color": MUTED}),
        ], style={"marginBottom": "8px"}),

        # DataTable
        dash_table.DataTable(
            id="abbr-table",
            data=ROWS,
            columns=COLUMNS,
            sort_action="native",
            page_action="none",
            style_table={"width": "100%", "overflowX": "auto", "maxWidth": "800px"},
            style_cell={
                "padding": "8px",
                "borderBottom": "1px solid #eee",
                "fontSize": "15px",
            },
            style_cell_conditional=[
                {"if": {"column_id": "Category"}, "width": "30%", "textAlign": "left", "fontWeight": 500},
                {"if": {"column_id": "Abbrev"},   "width": "20%", "textAlign": "center", "fontWeight": 600},
                {"if": {"column_id": "Meaning"},  "width": "50%", "textAlign": "left"},
            ],
            style_header={
                "backgroundColor": "#f7f7f7",
                "fontWeight": 600,
                "borderBottom": "1px solid #eaeaea",
            },
        ),
    ],
)

# ---------------- Callback ----------------
def _matches(text: str, q: str) -> bool:
    q = (q or "").strip().lower()
    if not q:
        return True
    terms = [t for t in q.split() if t]
    text = (text or "").lower()
    return all(t in text for t in terms)

@callback(
    Output("abbr-table", "data"),
    Output("abbr-count", "children"),
    Input("abbr-search", "value"),
)
def filter_abbreviations(q):
    filtered = [r for r in ROWS if _matches(f"{r['Category']} {r['Abbrev']} {r['Meaning']}", q)]
    return filtered, f"{len(filtered)} of {len(ROWS)} shown"
