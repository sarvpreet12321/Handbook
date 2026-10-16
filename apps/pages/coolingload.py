# apps/pages/cooling_loads.py
from dash import register_page, html, dcc, dash_table, Input, Output, callback
from apps.shared.ui import BRAND, MUTED, BLACK  # remove if you don't use these

register_page(__name__, path="/coolingload", name="Cooling Loads")


# ---- Data (W/m², air-conditioned area) ----
ROWS = [
    {"Occupancy": "Apartments, Residence",         "Cooling Load (W/m²)": 120},
    {"Occupancy": "Auditorium",                    "Cooling Load (W/m²)": 280},
    {"Occupancy": "Banks",                         "Cooling Load (W/m²)": 175},
    {"Occupancy": "Hairdresser",                   "Cooling Load (W/m²)": 215},
    {"Occupancy": "Beauty Shop",                   "Cooling Load (W/m²)": 260},
    {"Occupancy": "Cafeteria",                     "Cooling Load (W/m²)": 350},
    {"Occupancy": "Classroom",                     "Cooling Load (W/m²)": 95},
    {"Occupancy": "Clinic",                        "Cooling Load (W/m²)": 190},
    {"Occupancy": "Clothing Store",                "Cooling Load (W/m²)": 165},
    {"Occupancy": "Computer Room",                 "Cooling Load (W/m²)": 480},

    {"Occupancy": "Conference Room",               "Cooling Load (W/m²)": 275},
    {"Occupancy": "Department Store",              "Cooling Load (W/m²)": None},  # “-” in the scan
    {"Occupancy": "Basement",                      "Cooling Load (W/m²)": 125},
    {"Occupancy": "Main Floor",                    "Cooling Load (W/m²)": 150},
    {"Occupancy": "Upper Floors",                  "Cooling Load (W/m²)": 125},

    {"Occupancy": "Factory - Light Manufacture",   "Cooling Load (W/m²)": 275},
    {"Occupancy": "Factory - Heavy Manufacture",   "Cooling Load (W/m²)": 490},
    {"Occupancy": "Food Stores",                   "Cooling Load (W/m²)": 160},
    {"Occupancy": "Hotel & Motel Rooms",           "Cooling Load (W/m²)": 120},
    {"Occupancy": "Laboratory",                    "Cooling Load (W/m²)": 130},

    {"Occupancy": "Library",                       "Cooling Load (W/m²)": 150},
    {"Occupancy": "Mall",                          "Cooling Load (W/m²)": 135},
    {"Occupancy": "Medical Offices",               "Cooling Load (W/m²)": 185},
    {"Occupancy": "Milk Bars, Fast Food",          "Cooling Load (W/m²)": 270},
    {"Occupancy": "Office - General (Perimeter)",  "Cooling Load (W/m²)": 170},
    {"Occupancy": "Office - General (Interior)",   "Cooling Load (W/m²)": 100},
    {"Occupancy": "Office - Private",              "Cooling Load (W/m²)": 180},
    {"Occupancy": "Post Office",                   "Cooling Load (W/m²)": 180},
    {"Occupancy": "Restaurants",                   "Cooling Load (W/m²)": 330},
    {"Occupancy": "Shoe Store",                    "Cooling Load (W/m²)": 185},
    {"Occupancy": "Super Market",                  "Cooling Load (W/m²)": 160},
    {"Occupancy": "Theatre",                       "Cooling Load (W/m²)": 280},
]

COLUMNS = [
    {"name": "Occupancy",             "id": "Occupancy",             "type": "text"},
    {"name": "Cooling Load (W/m²)",   "id": "Cooling Load (W/m²)",   "type": "numeric"},
]

# -------- Layout --------
layout = html.Div(
    style={"width": "100%", "padding": "16px", "fontFamily": "Segoe UI, Inter, Arial", "color": BLACK},
    children=[
        html.Div(
            style={"display": "flex", "alignItems": "center", "gap": "14px", "marginBottom": "10px"},
            children=[
                html.Div(style={"width": "12px", "height": "28px", "backgroundColor": BRAND, "borderRadius": "6px"}),
                html.H2("Cooling Load Check Figures", style={"margin": 0}),
            ],
        ),
        html.P("Indicative sensible cooling loads for common occupancies (air-conditioned area, W/m²).",
               style={"color": MUTED, "marginTop": 0, "marginBottom": "10px"}),

        # Search row
        html.Div([
            html.Label("Search occupancy", htmlFor="cl-search", style={"marginRight": "10px"}),
            dcc.Input(
                id="cl-search",
                type="text",
                placeholder="e.g. office, restaurant, factory",
                debounce=True,
                style={"width": "340px", "marginRight": "14px"}
            ),
            html.Span(id="cl-count", style={"color": MUTED}),
        ], style={"marginBottom": "8px"}),

        # Table
        dash_table.DataTable(
            id="cl-table",
            data=ROWS,
            columns=COLUMNS,
            sort_action="native",
            page_action="none",   # show all
            style_table={"width": "100%", "overflowX": "auto", "maxWidth": "900px"},
            style_cell={
                "padding": "10px",
                "borderBottom": "1px solid #eee",
                "fontSize": "15px",
            },
            style_cell_conditional=[
                {"if": {"column_id": "Occupancy"}, "width": "60%", "textAlign": "left"},
                {"if": {"column_id": "Cooling Load (W/m²)"}, "width": "40%", "textAlign": "right",
                 "fontVariantNumeric": "tabular-nums"},
            ],
            style_header={
                "backgroundColor": "#f7f7f7",
                "fontWeight": 600,
                "borderBottom": "1px solid #eaeaea",
            },
            # Show “—” for missing values (e.g., Department Store)
            cell_selectable=False,
        ),
        html.Div("Source: AIRAH Technical Handbook (2013), Cooling Load Check Figures.",
                 style={"color": MUTED, "marginTop": "10px"}),
    ],
)

# -------- Callbacks --------
def _matches(row_text: str, query: str) -> bool:
    """Return True if all query terms appear (case-insensitive) in the row_text."""
    q = (query or "").strip().lower()
    if not q:
        return True
    terms = [t for t in q.split() if t]
    text = (row_text or "").lower()
    return all(t in text for t in terms)

@callback(
    Output("cl-table", "data"),
    Output("cl-count", "children"),
    Input("cl-search", "value"),
)
def filter_rows(q):
    filtered = [
        # replace None with "—" for display
        {"Occupancy": r["Occupancy"],
         "Cooling Load (W/m²)": r["Cooling Load (W/m²)"] if r["Cooling Load (W/m²)"] is not None else "—"}
        for r in ROWS
        if _matches(r["Occupancy"], q)
    ]
    return filtered, f"{len(filtered)} of {len(ROWS)} shown"
