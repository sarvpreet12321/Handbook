from math import log10
from dash import register_page, html, dcc, Input, Output, callback, dash_table
from apps.shared.ui import section_card, input_box, BRAND, MUTED, BLACK

register_page(__name__, path="/air_diffusers", name="air_diffusers")

# ---- Table data ----
rows = [
    {"Air Quantity (L/s)": "Up to 50",  "Diffuser Neck Size (mm × mm)": "150 × 150", "Flexible Ductwork (Ø mm)": "150"},
    {"Air Quantity (L/s)": "55 to 80",  "Diffuser Neck Size (mm × mm)": "150 × 150", "Flexible Ductwork (Ø mm)": "200"},
    {"Air Quantity (L/s)": "85 to 110", "Diffuser Neck Size (mm × mm)": "225 × 225", "Flexible Ductwork (Ø mm)": "200"},
    {"Air Quantity (L/s)": "115 to 150","Diffuser Neck Size (mm × mm)": "225 × 225", "Flexible Ductwork (Ø mm)": "250"},
    {"Air Quantity (L/s)": "155 to 170","Diffuser Neck Size (mm × mm)": "300 × 300", "Flexible Ductwork (Ø mm)": "250"},
    {"Air Quantity (L/s)": "175 to 250","Diffuser Neck Size (mm × mm)": "300 × 300", "Flexible Ductwork (Ø mm)": "300"},
    {"Air Quantity (L/s)": "255 to 340","Diffuser Neck Size (mm × mm)": "375 × 375", "Flexible Ductwork (Ø mm)": "350"},
    {"Air Quantity (L/s)": "345 to 440","Diffuser Neck Size (mm × mm)": "450 × 450", "Flexible Ductwork (Ø mm)": "400"},
]

columns = [
    {"name": "Air Quantity (L/S)",              "id": "Air Quantity (L/s)"},
    {"name": "Diffuser Neck Size (mm x mm)",        "id": "Diffuser Neck Size (mm × mm)"},
    {"name": "Flexible Ductwork (Ø mm)",  "id": "Flexible Ductwork (Ø mm)"},
]

layout = html.Div(
    style={"width": "100%", "padding": "16px", "fontFamily": "Segoe UI, Inter, Arial", "color": BLACK},
    children=[
        # Page header
        html.Div(
            style={"display": "flex", "alignItems": "center", "gap": "14px", "marginBottom": "12px"},
            children=[
                html.Div(style={"width": "12px", "height": "28px", "backgroundColor": BRAND, "borderRadius": "6px"}),
                html.H2("Air Diffusers and Flexible Duct Figures", style={"margin": 0}),
            ],
        ),
        html.P("Selection guide for diffuser neck size and flexible duct diameter vs air quantity.",
               style={"color": MUTED, "marginTop": 0, "marginBottom": "10px"}),

        # Optional centered caption row like the screenshot's single 'c' header
        html.Div("", style={"textAlign": "center", "fontWeight": 600, "color": MUTED, "marginBottom": "6px"}),

        # Data table
        dash_table.DataTable(
            id="air-diffusers-table",
            data=rows,
            columns=columns,
            style_table={"width": "100%", "overflowX": "auto"},
            style_cell={
                "padding": "10px",
                "textAlign": "center",
                "border": "1px solid #eaeaea",
                "fontSize": "15px",
            },
            style_header={
                "backgroundColor": "#f7f7f7",
                "fontWeight": 600,
                "border": "1px solid #eaeaea",
            },
            style_as_list_view=True,
        ),

        # Typical Specification
        html.H3("Typical Specification", style={"marginTop": "24px"}),
        html.Ol([
            html.Li(
                "For tiled ceiling, all new S/A diffusers shall be 600 × 600 flat face ceiling diffuser "
                "complete with internally insulated header box, insulated flexible ductwork & spigot "
                "fitted with volume control damper."
            ),
            html.Li(
                "For plaster board ceiling, all new S/A diffusers shall be 450 × 450 bevel face ceiling "
                "diffuser complete with internally insulated header box, insulated flexible ductwork & "
                "spigot fitted with volume control damper."
            ),
        ], style={"lineHeight": "1.6", "maxWidth": "900px"}),
    ],
)
