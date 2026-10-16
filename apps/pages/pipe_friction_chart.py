# apps/pages/pipe_friction_chart.py
import numpy as np
import plotly.graph_objects as go
from dash import register_page, html, dcc, Input, Output, State, callback, ctx, no_update
from CoolProp.CoolProp import PropsSI

register_page(__name__, path="/pipe-friction-chart", name="Pipe Friction Chart")

PIPE_IDS_M = {"DN15":0.0138,"DN20":0.0180,"DN25":0.0235,"DN32":0.0300,"DN40":0.0368,"DN50":0.0476}

ROUGHNESS_PRESETS_MM = {
    "Glass (0.0003)": 0.0003,
    "Stainless (0.0010)"  : 0.0010,
    "Copper Type B (0.0015)"      : 0.0015,
    "PVC / HDPE (0.0050)"         : 0.0050,
    "Commercial steel (0.0260)"   : 0.0260,
    "Std wt steel ANSI B36.10 (0.0460)": 0.0460,
    "Galvanized iron (0.1500)"    : 0.1500,
    "Cast iron (0.2600)"          : 0.2600,
    "Custom…"                     : None,
}

def friction_factor(Re, eps, D):
    Re = np.asarray(Re); f = np.empty_like(Re, float)
    lam = Re < 2300
    f[lam] = 64.0 / np.maximum(Re[lam], 1e-9)
    tur = ~lam
    term = (eps/(3.7*D))**1.11 + 6.9/np.maximum(Re[tur],1.0)
    f[tur] = (-1.8*np.log10(term))**-2
    return f

def dp_per_m_for_diameter(Q_m3s, D, rho, mu, eps):
    A = np.pi*(D**2)/4.0
    v = Q_m3s/A
    Re = rho*v*D/mu
    f  = friction_factor(Re, eps, D)
    return f*(rho*v*v)/(2.0*D)

def make_figure(selected_sizes, T_C, eps_m):
    T_K = T_C + 273.15
    rho = PropsSI("D","T",T_K,"P",101325,"Water")
    mu  = PropsSI("V","T",T_K,"P",101325,"Water")
    Q_ls  = np.logspace(-1.3, 2.0, 220)
    Q_m3s = Q_ls/1000.0
    fig = go.Figure()
    for label in selected_sizes:
        D = PIPE_IDS_M[label]
        dpL = dp_per_m_for_diameter(Q_m3s, D, rho, mu, eps_m)
        fig.add_trace(go.Scatter(x=Q_ls, y=dpL, mode="lines",
                                 name=f"{label} (ID={D*1000:.1f} mm)",
                                 hovertemplate="Q=%{x:.3g} L/s<br>Δp/L=%{y:.3g} Pa/m<extra></extra>"))
    fig.update_layout(
        xaxis=dict(type="log", title="Flow Q (L/s)"),
        yaxis=dict(type="log", title="Pressure drop Δp/L (Pa/m)"),
        template="plotly_white", legend_title_text="Pipe size (internal Ø)",
        margin=dict(l=60,r=20,t=30,b=50),
    )
    return fig, rho, mu

# --------------- Layout ---------------
layout = html.Div(style={"padding":"16px"}, children=[
    html.H2("Interactive Pipe Friction Chart — Water"),

    html.Div([
        html.Label("Pipe sizes"),
        dcc.Checklist(id="sizes",
                      options=[{"label":k,"value":k} for k in PIPE_IDS_M],
                      value=list(PIPE_IDS_M), inline=True),
        html.Div(style={"height":"8px"}),

        html.Div([
            html.Label("Water temperature (°C)"),
            html.Div([
                dcc.Slider(id="temp", min=0, max=60, step=1, value=10,
                           marks={i:str(i) for i in range(0,61,10)}, included=False),
                html.Div(id="temp-readout", style={"minWidth":"260px","textAlign":"right","color":"#555"})
            ], style={"display":"grid","gridTemplateColumns":"1fr auto","alignItems":"center","gap":"12px"}),
        ]),

        html.Div(style={"height":"8px"}),

        html.Label("Absolute roughness ε (mm)"),
        dcc.Dropdown(id="eps_preset",
                     options=[{"label":k,"value":k} for k in ROUGHNESS_PRESETS_MM],
                     value="Std wt steel ANSI B36.10 (0.0460)", clearable=False,
                     style={"width":"420px","marginBottom":"6px"}),

        html.Div([
            dcc.Slider(id="eps", min=0.0003, max=0.30, step=0.0001, value=0.0460,
                       marks={v:f"{v:.3f}" for v in [0.001,0.005,0.015,0.046,0.10,0.20,0.30]},
                       included=False),
            html.Div(id="eps-readout", style={"minWidth":"220px","textAlign":"right","color":"#555"})
        ], style={"display":"grid","gridTemplateColumns":"1fr auto","alignItems":"center","gap":"12px"}),

        html.Div(style={"height":"8px"}),

        html.Label("Overlay a state point"),
        html.Div([
            html.Span("Q (L/s)"),
            dcc.Input(id="Q_in", type="number", value=1.0, step=0.1,
                      style={"width":"110px","marginRight":"14px"}),
            html.Span("Δp/L (Pa/m)"),
            dcc.Input(id="dp_in", type="number", value=200.0, step=10.0,
                      style={"width":"110px","marginRight":"14px"}),
        ], style={"display":"flex","alignItems":"center","gap":"10px"}),
        html.Div(id="point-readout", style={"color":"#555","marginTop":"6px"}),
    ], style={"maxWidth":"1100px"}),

    dcc.Graph(id="pipe-chart", style={"height":"700px"}),
])

# --------------- Main chart callback (returns 4 outputs) ---------------
@callback(
    Output("pipe-chart", "figure"),
    Output("point-readout", "children"),
    Output("temp-readout", "children"),
    Output("eps-readout", "children"),
    Input("sizes", "value"),
    Input("temp", "value"),
    Input("eps", "value"),
    Input("Q_in", "value"),
    Input("dp_in", "value"),
)
def draw_chart(sizes, T_C, eps_mm, Q_in, dp_in):
    sizes = sizes or list(PIPE_IDS_M)
    eps_m = (eps_mm or 0.0460) * 1e-3
    fig, rho, mu = make_figure(sizes, T_C or 10.0, eps_m)

    temp_text = f"{(T_C or 10):.0f} °C  ·  ρ = {rho:.1f} kg/m³  ·  μ = {mu*1e3:.2f} mPa·s"
    eps_text  = f"ε = {eps_mm:.4f} mm"

    # No point → just return props
    if not (Q_in and dp_in and Q_in > 0 and dp_in > 0):
        props = f"ρ = {rho:.1f} kg/m³ · μ = {mu*1e3:.2f} mPa·s (water at {T_C or 10:.0f} °C)"
        return fig, html.Div(props, style={"color":"#555","marginTop":"6px"}), temp_text, eps_text

    # Overlay state point + size table
    fig.add_trace(go.Scatter(x=[Q_in], y=[dp_in], mode="markers",
                             marker=dict(size=10, symbol="x"),
                             name="State point",
                             hovertemplate="Q=%{x:.3g} L/s<br>Δp/L=%{y:.3g} Pa/m<extra></extra>"))

    qs = (Q_in or 0)/1000.0
    header = html.Thead(html.Tr([html.Th("Size"), html.Th("ID (mm)"),
                                 html.Th("Velocity (m/s)"), html.Th("Δp/L (Pa/m)"),
                                 html.Th("Δp (kPa/100 m)")]))
    rows = []
    for label in sizes:
        D = PIPE_IDS_M[label]; A = np.pi*(D**2)/4.0
        v = qs/A if A>0 else 0.0
        Re = rho*v*D/mu; f = friction_factor(Re, eps_m, D)
        dp_m = f*(rho*v*v)/(2.0*D)
        rows.append(html.Tr([html.Td(label), html.Td(f"{D*1000:.1f}"),
                             html.Td(f"{v:.2f}"), html.Td(f"{dp_m:,.0f}"),
                             html.Td(f"{dp_m*100/1000:.1f}")]))
    table = html.Table([header, html.Tbody(rows)],
                       style={"borderCollapse":"collapse","marginTop":"10px","width":"100%","maxWidth":"900px"})

    return fig, table, temp_text, eps_text

# --------------- Sync preset <-> slider (single callback, no cycle) ---------------
@callback(
    Output("eps", "value"),
    Output("eps_preset", "value"),
    Input("eps_preset", "value"),
    Input("eps", "value"),
    prevent_initial_call=True,
)
def sync_roughness(preset_label, eps_val):
    trig = ctx.triggered_id
    if trig == "eps_preset":
        val = ROUGHNESS_PRESETS_MM.get(preset_label)
        if val is None:
            return no_update, "Custom…"
        return float(val), preset_label
    elif trig == "eps":
        # try to match a named preset
        label = "Custom…"
        for k, v in ROUGHNESS_PRESETS_MM.items():
            if v is not None and abs((eps_val or 0) - v) <= 1e-6:
                label = k; break
        return eps_val, label
    return no_update, no_update
