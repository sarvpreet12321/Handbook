# apps/pages/ductulator.py
from dash import register_page, html, dcc, Input, Output, State, callback, no_update, dash_table
from apps.shared.ui import BRAND, MUTED, BLACK, section_card, input_box
import math

register_page(__name__, path="/ductwork-rules", name="ductwork-rules")


# ---------------- Data ----------------
ROWS = [
    {"Item": "Ductwork – Supply",                                  "Rule": "≤ 1.2 Pa/m friction (to a maximum of 7.0 m/s)"},
    {"Item": "Ductwork – Return",                                  "Rule": "≤ 1.2 Pa/m friction (to a maximum of 6.5 m/s)"},
    {"Item": "Ductwork – Return (behind R/A grille)",              "Rule": "3.0 m/s (check noise level in manufacturer literature)"},
    {"Item": "Ductwork – Exhaust",                                 "Rule": "6.5 m/s"},
    {"Item": "Ductwork – Flexible Supply",                         "Rule": "3.5 m/s"},
    {"Item": "Neck velocity for supply air register",              "Rule": "2.5 m/s"},
    {"Item": "Coil face velocity – Cooling",                       "Rule": "2.25 m/s (check pressure in manufacturer literature)"},
    {"Item": "Coil face velocity – Heating",                       "Rule": "3.5 m/s (check pressure in manufacturer literature)"},
    {"Item": "Air filter face velocity",                           "Rule": "1.8 – 2.5 m/s (check pressure in manufacturer literature)"},
    {"Item": "Louvres face velocity – Outside air intake",         "Rule": "1.8 – 2.0 m/s (max) (check pressure in manufacturer literature)"},
    {"Item": "Louvres – Exhaust (velocity through free area)",     "Rule": "2.5 m/s (check pressure in manufacturer literature)"},
    {"Item": "Door grille – Face velocity",                        "Rule": "1.25 m/s (check noise level in manufacturer literature)"},
    {"Item": "Volume control damper (incl. MVCD)",                 "Rule": "6.0 – 9.0 m/s"},
    {"Item": "Relief air grille – Maximum pressure drop",          "Rule": "15 Pa"},
    {"Item": "Straight duct pressure loss (ductulator)",           "Rule": "0.8 – 1.2 Pa/m"},
]

COLUMNS = [
    {"name": "Item", "id": "Item"},
    {"name": "Rule / Target", "id": "Rule"},
]

# ---------------- Layout ----------------
layout = html.Div(
    style={"width": "100%", "padding": "16px", "fontFamily": "Segoe UI, Inter, Arial", "color": BLACK},
    children=[
        # Header
        html.Div(
            style={"display": "flex", "alignItems": "center", "gap": "14px", "marginBottom": "10px"},
            children=[
                html.Div(style={"width": "12px", "height": "28px", "backgroundColor": BRAND, "borderRadius": "6px"}),
                html.H2("Ductwork Rules of Thumb", style={"margin": 0}),
            ],
        ),
        html.P("Quick reference velocities, friction limits and typical targets.",
               style={"color": MUTED, "marginTop": 0, "marginBottom": "10px"}),

        # Search
        html.Div([
            html.Label("Search", htmlFor="rules-search", style={"marginRight": "10px"}),
            dcc.Input(
                id="rules-search",
                type="text",
                placeholder="e.g. supply, grille, 1.2 Pa/m, 3.5 m/s",
                debounce=True,
                style={"width": "360px", "marginRight": "14px"}
            ),
            html.Span(id="rules-count", style={"color": MUTED}),
        ], style={"marginBottom": "8px"}),

        # Table
        dash_table.DataTable(
            id="rules-table",
            data=ROWS,
            columns=COLUMNS,
            sort_action="native",
            page_action="none",
            style_table={"width": "100%", "overflowX": "auto", "maxWidth": "1000px"},
            style_cell={
                "padding": "10px",
                "borderBottom": "1px solid #eee",
                "fontSize": "15px",
            },
            style_cell_conditional=[
                {"if": {"column_id": "Item"}, "width": "52%", "textAlign": "left", "fontWeight": 500},
                {"if": {"column_id": "Rule"}, "width": "48%", "textAlign": "right", "fontVariantNumeric": "tabular-nums"},
            ],
            style_header={
                "backgroundColor": "#f7f7f7",
                "fontWeight": 600,
                "borderBottom": "1px solid #eaeaea",
            },
        ),
    ],
)

# ---------------- Callbacks ----------------
def _matches(text: str, q: str) -> bool:
    q = (q or "").strip().lower()
    if not q:
        return True
    terms = [t for t in q.split() if t]
    text = (text or "").lower()
    return all(t in text for t in terms)

@callback(
    Output("rules-table", "data"),
    Output("rules-count", "children"),
    Input("rules-search", "value"),
)
def filter_rules(q):
    filtered = [r for r in ROWS if _matches(f"{r['Item']} {r['Rule']}", q)]
    return filtered, f"{len(filtered)} of {len(ROWS)} shown"