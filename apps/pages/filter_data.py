# apps/pages/filterdata.py
from __future__ import annotations
from pathlib import Path
import re
import pandas as pd
from dash import register_page, html, dcc, dash_table, Input, Output, State, callback

register_page(__name__, path="/filterdata", name="Filter Data")

# ---------- Locate CSV ----------
def find_csv() -> Path | None:
    here = Path(__file__).resolve()
    for p in [
        here.parents[2] / "app"  / "assets" / "airepleat_data.csv",
        here.parents[2] / "apps" / "assets" / "airepleat_data.csv",
        here.parents[2] / "assets" / "airepleat_data.csv",
    ]:
        if p.exists():
            return p
    return None

CSV_PATH = find_csv()
if CSV_PATH is None:
    raise FileNotFoundError("Could not find airepleat_data.csv in app/assets or apps/assets")

# ---------- Parse “H x W x D” ----------
_NUM = re.compile(r"[-+]?\d*\.?\d+")

def parse_triplet(s: str) -> tuple[float, float, float]:
    if s is None:
        return float("nan"), float("nan"), float("nan")
    nums = _NUM.findall(str(s))
    vals = [float(n) for n in nums[:3]]
    while len(vals) < 3:
        vals.append(float("nan"))
    return tuple(vals)  # (H, W, D)

# ---------- Load & normalise ----------
def load_data() -> pd.DataFrame:
    df = pd.read_csv(CSV_PATH)

    # exact headers you provided
    df = df.rename(columns={
        "Product code":             "product_code",
        "Nominal Size (mm)":        "nominal_str_src",
        "Actual Size (mm)":         "actual_str_src",
        "Airflow Capacity (L/sec)": "airflow_lps",
        "Initial Resistance (Pa)":  "initial_res_pa",
        "Filter Classification":    "classification",
    })

    nH, nW, nD = zip(*df["nominal_str_src"].map(parse_triplet))
    aH, aW, aD = zip(*df["actual_str_src"].map(parse_triplet))
    df["nom_h"], df["nom_w"], df["nom_d"] = nH, nW, nD
    df["act_h"], df["act_w"], df["act_d"] = aH, aW, aD

    # pretty strings for display
    def fmt_trip(h, w, d):
        return f"{int(round(h))}×{int(round(w))}×{int(round(d))}"
    df["nominal_str"] = [fmt_trip(h, w, d) for h, w, d in zip(df.nom_h, df.nom_w, df.nom_d)]
    df["actual_str"]  = [fmt_trip(h, w, d) for h, w, d in zip(df.act_h, df.act_w, df.act_d)]

    # keep rows that parsed
    mask = df[["act_h", "act_w", "act_d"]].notna().all(axis=1)
    return df.loc[mask].copy()

DF = load_data()
CLS_OPTIONS = sorted([c for c in DF["classification"].dropna().unique()])

# ---------- Small UI helpers ----------
def num_input(i, value=None, step=1, width="130px", placeholder=None):
    return dcc.Input(id=i, type="number", value=value, step=step,
                     placeholder=placeholder, style={"width": width})

# ---------- Layout ----------
layout = html.Div(
    style={"width": "100%", "maxWidth": "1200px", "margin": "20px auto",
           "fontFamily": "Segoe UI, Inter, Arial"},
    children=[
        html.H2("AirePleat — Performance Table with Filters"),

        # Filters grid
        html.Div(style={
            "display": "grid",
            "gridTemplateColumns": "240px 1fr",
            "columnGap": "12px",
            "rowGap": "8px",
            "alignItems": "center",
            "marginBottom": "8px",
        }, children=[
            html.Div(html.B("Product code contains")),
            num_input("q-code", value=None, step=1, width="220px", placeholder="e.g. 8001"),

            html.Div(html.B("Classification")),
            dcc.Dropdown(id="q-class", options=[{"label": c, "value": c} for c in CLS_OPTIONS],
                         value=[], multi=True, placeholder="Any"),

            html.Div(html.B("Airflow Capacity (L/s)")),
            html.Div([
                html.Span("min", style={"marginRight": "6px"}), num_input("q-af-min", None, 1, "110px"),
                html.Span("max", style={"margin":"0 6px 0 12px"}), num_input("q-af-max", None, 1, "110px"),
            ], style={"display": "flex", "alignItems": "center"}),

            html.Div(html.B("Initial Resistance (Pa)")),
            html.Div([
                html.Span("min", style={"marginRight": "6px"}), num_input("q-r-min", None, 1, "110px"),
                html.Span("max", style={"margin":"0 6px 0 12px"}), num_input("q-r-max", None, 1, "110px"),
            ], style={"display": "flex", "alignItems": "center"}),

            html.Div(html.B("Size basis")),
            dcc.RadioItems(
                id="q-size-basis",
                options=[{"label": "Actual (H×W×D)", "value": "actual"},
                         {"label": "Nominal (H×W×D)", "value": "nominal"}],
                value="actual", inline=True
            ),

            html.Div(html.B("Target size (mm) & tolerance (±)")),
            html.Div([
                num_input("q-h", None, 1, "110px", "H"),
                num_input("q-w", None, 1, "110px", "W"),
                num_input("q-d", None, 1, "110px", "D"),
                html.Span("tol ±", style={"margin":"0 6px 0 12px"}),
                num_input("q-tol", 10, 1, "90px", "mm"),
            ], style={"display": "flex", "alignItems": "center", "gap": "8px"}),

            html.Div(),
            html.Div("Tip: Leave filters blank to show the full table. "
                     "If H/W/D entered, rows are filtered by tolerance and sorted by closeness."),
        ]),

        html.Div(id="summary", style={"margin": "8px 0", "color": "#444"}),

        dash_table.DataTable(
            id="tbl",
            columns=[
                {"name":"Product code",       "id":"product_code"},
                {"name":"Nominal Size (mm)",  "id":"nominal_str"},
                {"name":"Actual Size (mm)",   "id":"actual_str"},
                {"name":"Airflow (L/s)",      "id":"airflow_lps", "type":"numeric", "format":{"specifier":",.0f"}},
                {"name":"Initial Res (Pa)",   "id":"initial_res_pa", "type":"numeric"},
                {"name":"Classification",     "id":"classification"},
                {"name":"Δ size (mm)",        "id":"delta_str"},
            ],
            # show the whole table initially
            data=DF.assign(delta_str="").to_dict("records"),
            page_size=15,
            sort_action="native",
            filter_action="none",
            style_table={"marginTop":"4px","overflowX":"auto"},
            style_cell={"fontSize":"14px","padding":"6px"},
            style_header={"fontWeight":"600","backgroundColor":"#f2f2f2"},
        ),

        html.Div(f"Loaded: {CSV_PATH}", style={"marginTop":"8px","color":"#777","fontSize":"12px"}),
    ]
)

# ---------- Filtering & sorting ----------
@callback(
    Output("tbl", "data"),
    Output("summary", "children"),
    Input("q-code", "value"),
    Input("q-class", "value"),
    Input("q-af-min", "value"), Input("q-af-max", "value"),
    Input("q-r-min", "value"),  Input("q-r-max", "value"),
    Input("q-size-basis", "value"),
    Input("q-h", "value"), Input("q-w", "value"), Input("q-d", "value"),
    Input("q-tol", "value"),
)
def apply_filters(code_like, classes, af_min, af_max, r_min, r_max,
                  basis, H, W, D, tol):
    df = DF.copy()

    # --- column filters (headers) ---
    if code_like not in (None, ""):
        df = df[df["product_code"].str.contains(str(code_like), case=False, na=False)]

    if classes:
        df = df[df["classification"].isin(classes)]

    if af_min is not None:
        df = df[df["airflow_lps"] >= float(af_min)]
    if af_max is not None:
        df = df[df["airflow_lps"] <= float(af_max)]

    if r_min is not None:
        df = df[df["initial_res_pa"] >= float(r_min)]
    if r_max is not None:
        df = df[df["initial_res_pa"] <= float(r_max)]

    # --- size filtering + closeness sorting ---
    # choose actual vs nominal numeric columns
    hcol, wcol, dcol = (("act_h", "act_w", "act_d") if basis == "actual"
                        else ("nom_h", "nom_w", "nom_d"))

    have_any_size = any(v is not None for v in (H, W, D))
    tol = float(tol or 0.0)

    if have_any_size:
        # Filter by tolerance when provided for each dimension
        if H is not None:
            df = df[df[hcol].between(float(H) - tol, float(H) + tol)]
        if W is not None:
            df = df[df[wcol].between(float(W) - tol, float(W) + tol)]
        if D is not None:
            df = df[df[dcol].between(float(D) - tol, float(D) + tol)]

        # compute distance only for dimensions provided
        dH = (df[hcol] - float(H)) .abs() if H is not None else 0.0
        dW = (df[wcol] - float(W)) .abs() if W is not None else 0.0
        dD = (df[dcol] - float(D)) .abs() if D is not None else 0.0
        df["dist"] = dH + dW + 2.0 * dD  # weight depth a bit
        df = df.sort_values(["dist", hcol, wcol])

        # show deltas
        def delta_str_row(r):
            parts = []
            if H is not None: parts.append(f"ΔH={int(round(abs(r[hcol]-H)))}")
            if W is not None: parts.append(f"ΔW={int(round(abs(r[wcol]-W)))}")
            if D is not None: parts.append(f"ΔD={int(round(abs(r[dcol]-D)))}")
            return ", ".join(parts)
        df["delta_str"] = [delta_str_row(r) for _, r in df.iterrows()]
    else:
        df["delta_str"] = ""

    # --- build output ---
    view = df[[
        "product_code", "nominal_str", "actual_str",
        "airflow_lps", "initial_res_pa", "classification", "delta_str"
    ]]
    data = view.to_dict("records")

    # summary
    size_note = ""
    if have_any_size:
        which = "Actual" if basis == "actual" else "Nominal"
        size_note = f" · {which} size near "
        trip = []
        if H is not None: trip.append(f"H={H:.0f}")
        if W is not None: trip.append(f"W={W:.0f}")
        if D is not None: trip.append(f"D={D:.0f}")
        size_note += "×".join(trip) + f" ±{tol:.0f} mm"
    summary = f"{len(view):,} matching rows" + size_note

    return data, summary
