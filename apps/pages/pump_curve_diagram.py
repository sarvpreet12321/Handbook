from dash import register_page, html, dcc, Input, Output, callback
import plotly.graph_objects as go
import numpy as np

register_page(__name__, path="/pump-curve-diagram", name="Pump Curve Diagram")

# -----------------------------------------------------
# Generate representative (illustrative, not real-pump) curve shapes
# -----------------------------------------------------
flow = np.linspace(0, 100, 200)  # relative flow units, 0-100%

shutoff_head = 60          # head at zero flow
head = shutoff_head * (1 - (flow / 118) ** 2)
head = np.clip(head, 0, None)

# Efficiency: parabola peaking at the Best Efficiency Point (BEP)
bep_flow = 60
efficiency = 78 * (1 - ((flow - bep_flow) / 70) ** 2)
efficiency = np.clip(efficiency, 0, None)

# Power draw: rises roughly with flow (kW, scaled to a 0-100 display range for comparison)
power = 12 + 0.55 * flow + 0.0025 * flow ** 2

# NPSH required: slowly rising curve, gets steep at high flow
npshr = 2 + 0.0009 * flow ** 2.4

curves = {
    "head": dict(
        y=head, name="Head (m)", color="#1f5fa8",
        hover="Head: %{y:.1f} m at flow %{x:.0f}%<extra></extra>",
        desc="Pressure the pump can generate at this flow rate. Falls as flow increases."
    ),
    "efficiency": dict(
        y=efficiency, name="Efficiency (%)", color="#2e8b57",
        hover="Efficiency: %{y:.0f}%% at flow %{x:.0f}%<extra></extra>",
        desc="How efficiently the pump converts input power into hydraulic work. Peaks at the Best Efficiency Point (BEP)."
    ),
    "power": dict(
        y=power, name="Power Draw (kW, relative)", color="#c0392b",
        hover="Power: %{y:.1f} kW (relative) at flow %{x:.0f}%<extra></extra>",
        desc="Motor power required at this flow rate. Generally rises as flow increases."
    ),
    "npshr": dict(
        y=npshr, name="NPSH Required (m)", color="#8e44ad",
        hover="NPSHr: %{y:.1f} m at flow %{x:.0f}%<extra></extra>",
        desc="Minimum suction pressure needed at the pump inlet to avoid cavitation. Rises with flow, often steeply near the right-hand edge."
    ),
}

CURVE_OPTIONS = [{"label": v["name"], "value": k} for k, v in curves.items()]
ALL_KEYS = list(curves.keys())

layout = html.Div(
    style={"width": "100%", "padding": "16px", "fontFamily": "Segoe UI, Inter, Arial"},
    children=[
        html.H2("Interactive Pump Performance Curve"),
        html.P(
            "This is an illustrative diagram, not real pump data. Use the checkboxes to show or hide each "
            "curve, and hover over any line to see what it represents.",
            style={"color": "#5f6368"}
        ),

        dcc.Checklist(
            id="curve-toggle",
            options=CURVE_OPTIONS,
            value=ALL_KEYS,
            inline=True,
            style={"marginBottom": "14px"},
            labelStyle={"marginRight": "18px"}
        ),

        dcc.Graph(id="pump-curve-graph", style={"height": "560px"}),

        html.Div(id="curve-legend-explainer", style={"marginTop": "10px", "fontSize": "14px", "color": "#333"}),
    ]
)


@callback(
    Output("pump-curve-graph", "figure"),
    Output("curve-legend-explainer", "children"),
    Input("curve-toggle", "value"),
)
def update_graph(selected):
    fig = go.Figure()

    for key in ALL_KEYS:
        if key not in selected:
            continue
        c = curves[key]
        fig.add_trace(go.Scatter(
            x=flow, y=c["y"],
            mode="lines",
            name=c["name"],
            line=dict(color=c["color"], width=3),
            hovertemplate=c["hover"],
        ))

    # Annotate shutoff head and BEP only if those curves are visible
    annotations = []
    if "head" in selected:
        annotations.append(dict(
            x=0, y=shutoff_head, text="Shutoff Head", showarrow=True,
            arrowhead=2, ax=40, ay=-30, font=dict(color="#1f5fa8")
        ))
    if "efficiency" in selected:
        bep_idx = int(np.argmax(efficiency))
        annotations.append(dict(
            x=flow[bep_idx], y=efficiency[bep_idx], text="Best Efficiency Point (BEP)",
            showarrow=True, arrowhead=2, ax=0, ay=-40, font=dict(color="#2e8b57")
        ))

    fig.update_layout(
        xaxis_title="Flow Rate (relative %)",
        yaxis_title="Relative scale (see legend/hover for real units)",
        template="plotly_white",
        legend=dict(orientation="h", y=-0.2),
        annotations=annotations,
        margin=dict(t=30, b=40),
    )

    explainer = html.Ul([
        html.Li([html.B(curves[k]["name"] + ": "), curves[k]["desc"]])
        for k in ALL_KEYS if k in selected
    ])

    return fig, explainer