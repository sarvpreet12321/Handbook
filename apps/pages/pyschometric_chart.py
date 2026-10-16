# apps/pages/psychrometric_chart.py
import numpy as np
import plotly.graph_objects as go
from dash import register_page, html, dcc, Input, Output, callback
from CoolProp.HumidAirProp import HAPropsSI
import dash

register_page(__name__, path="/psychrometric-chart", name="Psychrometric Chart")

P_ATM = 101325.0  # Pa
DB_MIN, DB_MAX = -10.0, 50.0
RH_MIN, RH_MAX = 0.0, 100.0

def _W_from_T_R(T_K, RH):
    return HAPropsSI("W", "T", float(T_K), "P", P_ATM, "R", float(RH))

def rh_curve(DB_C_array, RH):
    DB_C_array = np.atleast_1d(DB_C_array).astype(float)
    return np.array([_W_from_T_R(t + 273.15, RH) for t in DB_C_array])

def sat_curve(DB_C_array):
    return rh_curve(DB_C_array, 1.0)

def make_psychro_figure(tmin=DB_MIN, tmax=DB_MAX):
    db = np.linspace(tmin, tmax, 400)
    fig = go.Figure()
    for RH in np.arange(0.1, 1.0, 0.1):
        W = rh_curve(db, RH)
        fig.add_trace(go.Scatter(
            x=db, y=W*1000, mode="lines",
            hovertemplate="DB: %{x:.1f} °C<br>W: %{y:.2f} g/kg<extra>RH " + f"{int(RH*100)}%</extra>",
            name=f"RH {int(RH*100)}%"
        ))
    Wsat = sat_curve(db)
    fig.add_trace(go.Scatter(x=db, y=Wsat*1000, mode="lines", line=dict(width=3),
                             name="Saturation (100% RH)"))
    fig.update_layout(
        xaxis_title="Dry-bulb temperature (°C)",
        yaxis_title="Humidity ratio W (g/kg dry air)",
        yaxis=dict(range=[0,26]),
        template="plotly_white",
        legend_title="Relative Humidity",
        margin=dict(l=40, r=10, t=30, b=40),
    )
    return fig

layout = html.Div(
    style={"width": "100%", "padding": "16px"},
    children=[
        html.H2("Interactive Psychrometric Chart", style={"marginTop": 0}),

        # Controls
        html.Div([
            # Dry-bulb row
            html.Div([
                html.Label("Dry-bulb (°C)", htmlFor="db", style={"marginRight": "10px"}),
                dcc.Input(id="db_input", type="number", value=25, step=0.1,
                          debounce=True, style={"width": "110px", "marginRight": "14px"}),
                html.Div(  # wrap the slider; put flex on the wrapper, not on Slider
                    dcc.Slider(
                        id="db",
                        min=DB_MIN, max=DB_MAX, step=1, value=25,
                        marks={i: str(i) for i in range(int(DB_MIN), int(DB_MAX)+1, 10)},
                        included=False,
                        updatemode="mouseup",
                        tooltip={"always_visible": False, "placement": "bottom"},
                    ),
                    style={"flex": "1"}
                ),
            ], style={"display": "flex", "alignItems": "center", "gap": "8px", "marginBottom": "14px"}),

            # RH row
            html.Div([
                html.Label("Relative Humidity (%)", htmlFor="rh", style={"marginRight": "10px"}),
                dcc.Input(id="rh_input", type="number", value=50, step=0.1,
                          debounce=True, style={"width": "110px", "marginRight": "14px"}),
                html.Div(
                    dcc.Slider(
                        id="rh",
                        min=RH_MIN, max=RH_MAX, step=1, value=50,
                        marks={i: str(i) for i in range(int(RH_MIN), int(RH_MAX)+1, 10)},
                        included=False,
                        updatemode="mouseup",
                        tooltip={"always_visible": False, "placement": "bottom"},
                    ),
                    style={"flex": "1"}
                ),
            ], style={"display": "flex", "alignItems": "center", "gap": "8px"}),

            html.Div(id="state-readout", style={"marginTop": "8px", "color": "#555"}),
        ], style={"maxWidth": "900px"}),

        dcc.Graph(id="psy", figure=make_psychro_figure(), style={"height": "650px"}),
    ]
)

@callback(
    Output("psy", "figure"),
    Output("state-readout", "children"),
    Output("db", "value"),
    Output("db_input", "value"),
    Output("rh", "value"),
    Output("rh_input", "value"),
    Input("db", "value"),
    Input("db_input", "value"),
    Input("rh", "value"),
    Input("rh_input", "value"),
)
def update_chart(db_slider, db_input_val, rh_slider, rh_input_val):
    # robust ctx across Dash versions
    ctx = getattr(dash, "ctx", dash.callback_context)
    trig = ctx.triggered[0]["prop_id"].split(".")[0] if ctx.triggered else None

    db_val = db_input_val if trig == "db_input" else db_slider
    rh_val = rh_input_val if trig == "rh_input" else rh_slider

    if db_val is None: db_val = db_input_val if db_input_val is not None else 25.0
    if rh_val is None: rh_val = rh_input_val if rh_input_val is not None else 50.0

    # clamp
    try: db_val = float(db_val)
    except (TypeError, ValueError): db_val = 25.0
    db_val = max(DB_MIN, min(DB_MAX, db_val))

    try: rh_val = float(rh_val)
    except (TypeError, ValueError): rh_val = 50.0
    rh_val = max(RH_MIN, min(RH_MAX, rh_val))

    fig = make_psychro_figure()

    try:
        RH = rh_val / 100.0
        T_K = db_val + 273.15
        W   = HAPropsSI("W",   "T", T_K, "P", P_ATM, "R", RH)
        h   = HAPropsSI("H",   "T", T_K, "P", P_ATM, "R", RH) / 1000.0
        twb = HAPropsSI("Twb", "T", T_K, "P", P_ATM, "R", RH) - 273.15
        v   = HAPropsSI("V",   "T", T_K, "P", P_ATM, "R", RH)

        fig.add_trace(go.Scatter(
            x=[db_val], y=[W*1000.0],
            mode="markers", marker=dict(size=10),
            name="State point",
            hovertemplate=f"DB: {db_val:.1f} °C<br>RH: {rh_val:.0f}%<br>W: {W*1000:.2f} g/kg<extra></extra>"
        ))
        readout = (
            f"h = {h:.2f} kJ/kg_da · "
            f"W = {W*1000:.2f} g/kg · "
            f"Twb = {twb:.2f} °C · "
            f"v = {v:.3f} m³/kg"
        )
    except Exception as e:
        readout = f"State not defined for the selected inputs. ({e})"

    return fig, readout, db_val, db_val, rh_val, rh_val

