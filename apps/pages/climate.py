# apps/pages/climate_arcgis.py
from dash import register_page, html

register_page(__name__, path="/climate-arcgis", name="Climate Zones (ArcGIS)")


# --- palette for this table--------
COL_LHS   = "#cfe5c8"  # light green (left target column)
COL_INT   = "#f7d56a"  # amber header (Internal Ductliner group band)
COL_INT_SUB = "#f5c739"  # darker amber for subheaders
COL_EXT   = "#b9d7f0"  # blue header (External Ductwrap group band)
COL_EXT_SUB = "#9ec4e6"  # darker blue for subheaders
COL_OR    = "#fff4db"  # pale separator band

# --- data mapped from the scan ---
TARGETS = ["R1.0", "R1.2", "R1.6", "R2.0", "R2.4", "R3.0", "R3.4"]

# Internal ductliner (all Supertel with thickness and resulting R_MAT)
INTERNAL = [
    {"product": "Supertel", "thk": "40 mm",       "r": "R1.2"},  # for target R1.0
    {"product": "Supertel", "thk": "40 mm",       "r": "R1.2"},
    {"product": "Supertel", "thk": "63 mm",       "r": "R1.8"},
    {"product": "Supertel", "thk": "75 mm",       "r": "R2.2"},
    {"product": "Supertel", "thk": "100 mm",      "r": "R3.0"},
    {"product": "Supertel", "thk": "100 mm",      "r": "R3.0"},
    {"product": "Supertel", "thk": "2×63 mm",   "r": "R3.6"},
]

# External ductwrap – option A (Multitel) and option B (Flexitel)
EXT_A = [  # Multitel
    {"product": "Multitel", "thk": "38 mm",   "r": "R1.0"},
    {"product": "Multitel", "thk": "50 mm",   "r": "R1.3"},
    {"product": "Multitel", "thk": "75 mm",   "r": "R2.0"},
    {"product": "Multitel", "thk": "75 mm",   "r": "R2.0"},
    {"product": "Multitel", "thk": "2×50 mm","r": "R2.6"},
    {"product": "",         "thk": "",        "r": ""},       # blanks for higher targets (as per scan)
    {"product": "",         "thk": "",        "r": ""},
]

EXT_B = [  # Flexitel
    {"product": "Flexitel", "thk": "38 mm",   "r": "R1.1"},
    {"product": "Flexitel", "thk": "50 mm",   "r": "R1.4"},
    {"product": "Flexitel", "thk": "75 mm",   "r": "R2.1"},
    {"product": "Flexitel", "thk": "75 mm",   "r": "R2.1"},
    {"product": "Flexitel", "thk": "2×50 mm","r": "R2.8"},
    {"product": "",         "thk": "",        "r": ""},
    {"product": "",         "thk": "",        "r": ""},
]



# --- colours ---
ZONE_COLOURS = {
    1: "#f6a367",  # orange
    2: "#f6d34a",  # yellow
    3: "#f7e7a7",  # pale yellow
    4: "#dcecc7",  # light green
    5: "#c2dfb4",  # green
    6: "#9fc6e8",  # light blue
    7: "#5f8ec9",  # blue
    8: "#cfd8e8",  # light blue/grey
}
HDR_BG = "#f5b44a"   # header “Location”
BAND_BG = "#f6efe5"  # band for BCA/NCC labels

def zone_cell(val, z):
    return html.Td(val, style={
        "textAlign": "center",
        "padding": "6px 10px",
        "background": ZONE_COLOURS[z],
        "border": "1px solid #ccc",
        "whiteSpace": "nowrap",
    })

# --- helpers ---

def left_cell(text, *, bold=False, bg=None, style=None, **attrs):
    base_style = {
        "padding": "6px 10px",
        "border": "1px solid #ccc",
        "whiteSpace": "nowrap",
    }
    if bg:
        base_style["background"] = bg
    if bold:
        base_style["fontWeight"] = 600
    if style:
        base_style.update(style)
    # attrs may include rowSpan, colSpan, id, className, etc.
    return html.Td(text, style=base_style, **attrs)

def group_header(name, rowspan=3):
    # rowSpan is an allowed Td prop; vertical alignment goes in style
    return left_cell(
        name, bold=True, bg=BAND_BG,
        rowSpan=rowspan,
        style={"verticalAlign": "middle"}
    )

# --- data from the image ---
BCA_2010 = {
    "Conditioned Space": ["R1.2", "R1.2", "R1.2", "R1.0", "R1.2", "R1.0", "R1.0", "R1.6"],
    "Exposed to Sun":    ["R3.0", "R3.0", "R3.0", "R3.0", "R3.0", "R3.0", "R3.0", "R3.4"],
    "All other":         ["R2.0", "R2.0", "R2.0", "R2.0", "R2.0", "R2.0", "R2.0", "R2.4"],
}
NCC_2011 = {
    "Conditioned Space": ["R1.2", "R1.2", "R1.2", "R1.2", "R1.2", "R1.2", "R1.2", "R1.6"],
    "Exposed to Sun":    ["R3.0", "R3.0", "R3.0", "R3.0", "R3.0", "R3.0", "R3.0", "R3.4"],
    "All other":         ["R2.0", "R2.0", "R2.0", "R2.0", "R2.0", "R2.0", "R2.0", "R2.4"],
}

def rows_for(block_name, data_dict):
    keys = list(data_dict.keys())
    rows = []
    # first row carries the 3-row group header
    rows.append(html.Tr([
        group_header(block_name, rowspan=len(keys)),
        left_cell(keys[0], bg="#fff"),
        *[zone_cell(data_dict[keys[0]][i], i+1) for i in range(8)],
    ]))
    # remaining rows (no first column; rowSpan covers it)
    for k in keys[1:]:
        rows.append(html.Tr([
            left_cell(k, bg="#fff"),
            *[zone_cell(data_dict[k][i], i+1) for i in range(8)],
        ]))
    return rows


def rvalue_table():
    return html.Table(
        style={"borderCollapse": "collapse", "width": "100%", "maxWidth": "980px"},
        children=[
            html.Caption(
                "Ductwork – Minimum Required Material R-Value",
                style={"captionSide": "top", "textAlign": "left", "fontWeight": 700, "fontSize": "18px",
                    "marginBottom": "8px"}
            ),
            html.Thead([
                html.Tr([
                    left_cell("", bg="#eee"),
                    html.Th("Location", style={
                        "background": "#eee", "border": "1px solid #ccc",
                        "padding": "8px 10px", "textAlign": "left", "color": "#222"
                    }),
                    html.Th("Climate Zones", colSpan=8, style={
                        "background": "#eee", "border": "1px solid #ccc",
                        "padding": "8px 10px", "textAlign": "center"
                    }),
                ]),
                html.Tr([
                    left_cell("", bg="#eee"),
                    left_cell("", bg="#eee"),
                    *[html.Th(str(z), style={
                        "background": ZONE_COLOURS[z],
                        "border": "1px solid #bbb",
                        "padding": "6px 10px",
                        "width": "8%",
                    }) for z in range(1, 9)]
                ])
            ]),
            html.Tbody([
                *rows_for("BCA 2010", BCA_2010),
                *rows_for("NCC 2011", NCC_2011),
            ]),
        ]

    )




def rigid_duct_table():
    # header rows
    head_row1 = html.Tr([
        # left band (rowspan 2)
        html.Th(
            "Target BCA/NCC\nMinimum Material\nR-Value",
            style={
                "background": COL_LHS, "border": "1px solid #bbb", "padding": "8px 10px",
                "whiteSpace": "pre-line", "textAlign": "center", "verticalAlign": "middle"
            },
            rowSpan=2
        ),

        # internal group band
        html.Th(
            "Internal Ductliner",
            colSpan=3,
            style={"background": COL_INT, "border": "1px solid #bbb",
                "padding": "8px 10px", "textAlign": "center"}
        ),

        # OR separator (rowspan 2)
        html.Th("OR", rowSpan=2,
                style={"background": COL_OR, "border": "1px solid #bbb", "padding": "8px 10px",
                    "textAlign": "center", "verticalAlign": "middle", "width": "4%"}),

        # external group band — FIXED colSpan from 6 → 7
        html.Th(
            "External Ductwrap",
            colSpan=7,
            style={"background": COL_EXT, "border": "1px solid #bbb",
                "padding": "8px 10px", "textAlign": "center"}
        ),
    ])

    head_row2 = html.Tr([
        # Internal subheads
        html.Th("Product",   style={"background": COL_INT_SUB, "border": "1px solid #bbb", "padding": "6px 10px"}),
        html.Th("Thickness", style={"background": COL_INT_SUB, "border": "1px solid #bbb", "padding": "6px 10px"}),
        html.Th("Material R-Value (Rₘₐₜ)",
                style={"background": COL_INT_SUB, "border": "1px solid #bbb", "padding": "6px 10px"}),

        # External subheads (A)  – Product / Thickness / R
        html.Th("Product",   style={"background": COL_EXT_SUB, "border": "1px solid #bbb", "padding": "6px 10px"}),
        html.Th("Thickness", style={"background": COL_EXT_SUB, "border": "1px solid #bbb", "padding": "6px 10px"}),
        html.Th("Material R-Value (Rₘₐₜ)",
                style={"background": COL_EXT_SUB, "border": "1px solid #bbb", "padding": "6px 10px"}),

        # External separator “OR” (as a TH to match header look)
        html.Th("OR", style={"background": COL_OR, "border": "1px solid #bbb", "padding": "6px 10px", "width": "4%"}),

        # External subheads (B)
        html.Th("Product",   style={"background": COL_EXT_SUB, "border": "1px solid #bbb", "padding": "6px 10px"}),
        html.Th("Thickness", style={"background": COL_EXT_SUB, "border": "1px solid #bbb", "padding": "6px 10px"}),
        html.Th("Material R-Value (Rₘ)",
                style={"background": COL_EXT_SUB, "border": "1px solid #bbb", "padding": "6px 10px"}),
    ])

    # body rows
    body_rows = []
    for i, target in enumerate(TARGETS):
        row = html.Tr([
            html.Td(target, style={"background": COL_LHS, "border": "1px solid #bbb",
                                   "padding": "6px 10px", "textAlign": "center"}),

            # Internal
            html.Td(INTERNAL[i]["product"], style={"border": "1px solid #ccc", "padding": "6px 10px"}),
            html.Td(INTERNAL[i]["thk"],     style={"border": "1px solid #ccc", "padding": "6px 10px"}),
            html.Td(INTERNAL[i]["r"],       style={"border": "1px solid #ccc", "padding": "6px 10px"}),

            # OR
            html.Td("OR", style={"background": COL_OR, "border": "1px solid #bbb",
                                 "padding": "6px 10px", "textAlign": "center"}),

            # External A (Multitel)
            html.Td(EXT_A[i]["product"], style={"border": "1px solid #ccc", "padding": "6px 10px"}),
            html.Td(EXT_A[i]["thk"],     style={"border": "1px solid #ccc", "padding": "6px 10px"}),
            html.Td(EXT_A[i]["r"],       style={"border": "1px solid #ccc", "padding": "6px 10px"}),

            # External “OR”
            html.Td("OR", style={"background": COL_OR, "border": "1px solid #bbb",
                                 "padding": "6px 10px", "textAlign": "center"}),

            # External B (Flexitel)
            html.Td(EXT_B[i]["product"], style={"border": "1px solid #ccc", "padding": "6px 10px"}),
            html.Td(EXT_B[i]["thk"],     style={"border": "1px solid #ccc", "padding": "6px 10px"}),
            html.Td(EXT_B[i]["r"],       style={"border": "1px solid #ccc", "padding": "6px 10px"}),
        ])
        body_rows.append(row)

    return html.Table(
        style={"borderCollapse": "collapse", "width": "100%", "maxWidth": "1100px"},
        children=[
            html.Thead([head_row1, head_row2]),
            html.Tbody(body_rows),
        ],
    )

def flexible_duct_table():
    return html.Table(
        style={"borderCollapse": "collapse", "width": "100%", "maxWidth": "800px"},
        children=[
            html.Thead([
                # First header row
                html.Tr([
                    html.Th(
                        "Target BCA/NCC\nMinimum Material R-Value",
                        rowSpan=2,
                        style={
                            "background": "#c7e5c3", "border": "1px solid #bbb",
                            "padding": "8px 10px", "whiteSpace": "pre-line",
                            "textAlign": "center", "verticalAlign": "middle"
                        }
                    ),
                    html.Th(
                        "Flexible Duct Product Selector",
                        colSpan=3,
                        style={
                            "background": "#f7b77a", "border": "1px solid #bbb",
                            "padding": "8px 10px", "textAlign": "center"
                        }
                    ),
                ]),
                # Second header row
                html.Tr([
                    html.Th("Product", style={
                        "background": "#e67e22", "border": "1px solid #bbb",
                        "padding": "6px 10px", "textAlign": "center"
                    }),
                    html.Th("Thickness", style={
                        "background": "#e67e22", "border": "1px solid #bbb",
                        "padding": "6px 10px", "textAlign": "center"
                    }),
                    html.Th("Material R Value (Rₘ)", style={
                        "background": "#e67e22", "border": "1px solid #bbb",
                        "padding": "6px 10px", "textAlign": "center"
                    }),
                ]),
            ]),
            html.Tbody([
                html.Tr([
                    html.Td("R1.0", style={"border": "1px solid #ccc", "padding": "6px"}),
                    html.Td("Specitel", style={"border": "1px solid #ccc", "padding": "6px"}),
                    html.Td("40mm", style={"border": "1px solid #ccc", "padding": "6px"}),
                    html.Td("R1.0", style={"border": "1px solid #ccc", "padding": "6px"}),
                ]),
                html.Tr([
                    html.Td("R1.2", style={"border": "1px solid #ccc", "padding": "6px"}),
                    html.Td("Specitel", style={"border": "1px solid #ccc", "padding": "6px"}),
                    html.Td("50mm", style={"border": "1px solid #ccc", "padding": "6px"}),
                    html.Td("R1.2", style={"border": "1px solid #ccc", "padding": "6px"}),
                ]),
                html.Tr([
                    html.Td("R1.6", style={"border": "1px solid #ccc", "padding": "6px"}),
                    html.Td("Specitel", style={"border": "1px solid #ccc", "padding": "6px"}),
                    html.Td("65mm", style={"border": "1px solid #ccc", "padding": "6px"}),
                    html.Td("R1.6", style={"border": "1px solid #ccc", "padding": "6px"}),
                ]),
                html.Tr([
                    html.Td("R2.0", style={"border": "1px solid #ccc", "padding": "6px"}),
                    html.Td("Building Blanket", style={"border": "1px solid #ccc", "padding": "6px"}),
                    html.Td("90mm", style={"border": "1px solid #ccc", "padding": "6px"}),
                    html.Td("R2.0", style={"border": "1px solid #ccc", "padding": "6px"}),
                ]),
                html.Tr([
                    html.Td("R2.4", style={"border": "1px solid #ccc", "padding": "6px"}),
                    html.Td("Building Blanket", style={"border": "1px solid #ccc", "padding": "6px"}),
                    html.Td("110mm", style={"border": "1px solid #ccc", "padding": "6px"}),
                    html.Td("R2.5", style={"border": "1px solid #ccc", "padding": "6px"}),
                ]),
            ])
        ]
    )


def acoustic_table():
    BLUE = "#BDD7EE"
    ORANGE = "#F8CBAD"
    HEAD = "#FFC000"
    SECTION = "#FFE699"

    def hdr(text, colspan=1):
        return html.Th(text, colSpan=colspan, style={
            "background": HEAD, "border": "1px solid #bbb",
            "padding": "6px 8px", "textAlign": "center",
        })

    def section_row(title):
        return html.Tr([html.Td(title, colSpan=10, style={
            "background": SECTION, "border": "1px solid #bbb",
            "padding": "6px 8px", "fontWeight": 700,
        })])

    def data_row(product, thickness, freqs, nrc, colour):
        cells = [
            html.Td(product, style={"border": "1px solid #ccc", "padding": "6px 8px", "background": colour}),
            html.Td(thickness, style={"border": "1px solid #ccc", "padding": "6px 8px", "textAlign": "center", "background": colour}),
        ]
        for f in freqs:
            cells.append(html.Td(f, style={"border": "1px solid #ccc", "padding": "6px 8px", "textAlign": "center", "background": colour}))
        cells.append(html.Td(nrc, style={"border": "1px solid #ccc", "padding": "6px 8px", "textAlign": "center", "background": colour}))
        return html.Tr(cells)

    header = html.Thead([
        html.Tr([hdr("Product"), hdr("Thickness (mm)"), hdr("Frequency Hz", colspan=7), hdr("NRC")]),
        html.Tr([hdr(""), hdr(""), hdr("125"), hdr("250"), hdr("500"), hdr("1000"), hdr("2000"), hdr("4000"), hdr("5000"), hdr("")]),
    ])

    B, O = BLUE, ORANGE
    rows = [
        section_row("Supertel Ductliner"),
        data_row("Unfaced", 38, [0.15, 0.40, 0.85, 1.00, 1.00, 0.95, "na"], 0.85, B),
        data_row("Thermofoil HD perf", 38, [0.13, 0.43, 0.89, 1.02, 0.89, 0.82, 0.82], 0.80, O),
        data_row("Ultraphon", 38, [0.14, 0.45, 0.96, 1.00, 0.96, 0.93, 0.94], 0.84, O),
        data_row("Acoustituff", 38, [0.28, 0.53, 1.08, 0.88, 0.47, 0.25, 0.19], 0.74, O),
        data_row("Unfaced", 50, [0.20, 0.60, 1.00, 1.00, 1.00, 1.00, "na"], 0.95, B),
        data_row("Thermofoil HD Perf", 50, [0.23, 0.71, 0.99, 1.09, 0.97, 0.78, 0.59], 0.94, O),
        data_row("BMF", 50, [0.24, 0.62, 1.00, 1.07, 1.12, 1.15, 1.17], 0.95, O),
        data_row("HD Perf & Microfilm", 50, [0.32, 1.14, 0.94, 0.48, 0.22, 0.06, 0.03], 0.70, O),
        data_row("Acoustituff", 50, [0.25, 0.85, 1.00, 0.90, 0.55, 0.30, "na"], 0.85, O),
        data_row("Ultraphon", 50, [0.20, 0.65, 1.00, 1.00, 1.00, 1.00, "na"], 1.00, B),
        data_row("Unfaced", 75, [0.35, 1.00, 1.00, 1.00, 1.00, 1.00, "na"], 1.05, B),
        data_row("Thermofoil HD Perf", 75, [0.35, 1.00, 1.00, 1.00, 1.00, 1.00, "na"], 1.10, B),
        data_row("BMF", 75, [0.35, 1.00, 1.00, 1.00, 1.00, 1.00, "na"], 1.05, B),
        data_row("Ultraphon", 75, [0.35, 1.00, 1.00, 1.00, 1.00, 1.00, "na"], 1.10, B),
        data_row("Unfaced", 100, [0.50, 1.00, 1.00, 1.00, 1.00, 1.00, "na"], 1.15, B),
        data_row("Thermofoil HD Perf", 100, [0.65, 1.00, 1.00, 1.00, 1.00, 1.00, "na"], 1.15, B),

        section_row("Ultratel Ductliner"),
        data_row("Thermofoil HD Perf", 50, [0.20, 0.70, 1.00, 1.00, 1.00, 1.00, "na"], 1.05, B),
        data_row("BMF", 50, [0.25, 0.70, 1.13, 1.13, 1.12, 1.12, 1.12], 1.01, O),
        data_row("Acoustituff", 50, [0.30, 0.75, 0.90, 0.85, 0.65, 0.50, 0.60], 0.79, O),
        data_row("Thermofoil HD Perf", 75, [0.40, 1.00, 1.00, 1.00, 1.00, 0.95, "na"], 1.10, B),

        section_row("Fibertex Rockwool 350"),
        data_row("Unfaced", 25, [0.10, 0.25, 0.65, 0.85, 0.95, 0.95, "na"], 0.65, B),
        data_row("Thermofoil HD Perf", 25, [0.14, 0.38, 0.87, 1.07, 1.06, 0.90, 0.79], 0.85, O),
        data_row("BMF", 25, [0.15, 0.33, 0.74, 0.94, 1.03, 1.04, 0.98], 0.76, O),

        section_row("Fibertex Rockwool 450"),
        data_row("Unfaced", 50, [0.25, 0.75, 1.00, 1.00, 1.00, 1.00, "na"], 1.05, B),
        data_row("BMF", 50, [0.36, 0.76, 1.19, 1.09, 1.03, 1.04, 0.90], 1.01, O),
    ]

    return html.Table(
        style={"borderCollapse": "collapse", "width": "100%", "maxWidth": "1100px"},
        children=[header, html.Tbody(rows)],
    )


layout = html.Div(
    style={"padding": "8px"},
    children=[
        html.H2("Step A: Select the Climate Zone"),
        html.H3("Climate Zones (ArcGIS)"),
        html.Iframe(
            id="arcgis-embed",
            src="https://arcg.is/TbKyf0",           # your embed URL
            style={"width": "100%", "height": "80vh", "border": "0"},
            allow="fullscreen",                     # feature policy

        ),
        html.Hr(style={"margin":"24px 0"}),


        html.H2("Step B: Determine the Thermal Performance Required by the BCA/NCC"),
        html.P("Look up the R-Value required for the type of air-conditioning system and location of the duct."),
        rvalue_table(),
        html.Div("Note: All R-values are material R-values (R_MAT).",
                 style={"marginTop": "8px", "fontStyle": "italic", "color": "#444"}),


        html.H2("Step C"),
        html.P(
            "Specify the minimum recommended Bradford products to meet the BCA/NCC ductwork requirements from the tables below",
        ),

        html.H3("Rigid Duct Applications"),
        rigid_duct_table(),

        html.H3("Flexible Duct Applications"),
        flexible_duct_table(),

        html.Hr(style={"margin": "24px 0"}),
        html.H2("Section 5.1: Acoustic Performance Data"),
        html.P("Sound absorption is a key requirement of internal ductliners. The table below outlines "
               "the key acoustic performance characteristics of popular ductliner and facing combinations "
               "— useful when selecting a product in Step C above."),
        acoustic_table(),
        html.Div([
            html.Span(style={"display": "inline-block", "width": "14px", "height": "14px",
                              "backgroundColor": "#BDD7EE", "border": "1px solid #999",
                              "marginRight": "6px", "verticalAlign": "middle"}),
            html.Span("Sound absorption results in blue tested in accordance with AS ISO 354 - 2006 and NRC "
                      "results tested in accordance with ASTM C423-90A (note that the 5000Hz range is not "
                      "applicable for this Standard).", style={"verticalAlign": "middle"}),
        ], style={"marginTop": "10px", "fontSize": "13px"}),
        html.Div([
            html.Span(style={"display": "inline-block", "width": "14px", "height": "14px",
                              "backgroundColor": "#F8CBAD", "border": "1px solid #999",
                              "marginRight": "6px", "verticalAlign": "middle"}),
            html.Span("Sound absorption results in orange tested in accordance with AS1045:1998",
                      style={"verticalAlign": "middle"}),
        ], style={"marginTop": "6px", "fontSize": "13px"}),

    ],
)