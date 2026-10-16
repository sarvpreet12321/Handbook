# apps/pages/flexible_connections.py
from dash import register_page, html, dcc, Input, Output, callback
from apps.shared.ui import section_card, BRAND, BLACK

register_page(__name__, path="/flexible-connections", name="Flexible Connections")

# List of PDFs available for selection (only 2 now)
PDF_OPTIONS = [
    {"label": "Flexible Connection 1", "value": "FLEXIBLE-CONNECTION1.pdf"},
    {"label": "Flexible Connection 2", "value": "FLEXIBLE-CONNECTION2.pdf"},
]

layout = html.Div(
    style={"width": "100%", "margin": "20px auto", "fontFamily": "Segoe UI, Inter, Arial", "color": BLACK},
    children=[
        # Page header
        html.Div(
            style={"display": "flex", "alignItems": "center", "gap": "20px", "marginBottom": "18px"},
            children=[
                html.Div(style={"width": "12px", "height": "32px", "backgroundColor": BRAND, "borderRadius": "6px"}),
                html.H1("Flexible Connection Details", style={"margin": "0", "fontSize": "28px"}),
            ]
        ),

        # Dropdown for PDF selection (single selection only)
        html.Div([
            html.Label("Select PDF to view:"),
            dcc.Dropdown(
                id="pdf-selector",
                options=PDF_OPTIONS,
                multi=False,          # single selection
                value=PDF_OPTIONS[0]["value"],  # default selection
                style={"width": "100%"}
            )
        ], style={"marginBottom": "14px"}),

        # "Open in new tab" button — its href updates whenever the dropdown changes
        html.Div([
            html.A(
                "Open in new tab ↗",
                id="open-new-tab-link",
                href="",            # filled in by the callback below
                target="_blank",    # tells the browser to open a new tab
                style={
                    "display": "inline-block",
                    "padding": "8px 16px",
                    "backgroundColor": BRAND,
                    "color": "#fff",
                    "borderRadius": "8px",
                    "textDecoration": "none",
                    "fontWeight": "600",
                    "fontSize": "14px",
                }
            )
        ], style={"marginBottom": "20px"}),

        # Container for embedded PDF
        html.Div(id="pdf-container"),

        # Footer
        html.Div("AWP • Mechanical Handbook", style={"textAlign": "center", "color": "#5f6368", "marginTop": "22px"}),
    ]
)

# -----------------------
# Callback to display the selected PDF AND update the "open in new tab" link
# -----------------------
@callback(
    Output("pdf-container", "children"),
    Output("open-new-tab-link", "href"),
    Input("pdf-selector", "value")
)
def display_pdf(selected_pdf):
    if not selected_pdf:
        return html.Div("No PDF selected.", style={"textAlign": "center", "color": "#5f6368"}), ""

    pdf_url = f"/apps/assets/{selected_pdf}"

    iframe = html.Iframe(
        src=pdf_url,
        style={
            "width": "100%",
            "height": "600px",
            "border": "none",
            "borderRadius": "8px",
            "boxShadow": "0 2px 10px rgba(0,0,0,0.1)"
        }
    )

    return iframe, pdf_url