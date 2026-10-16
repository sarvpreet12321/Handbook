# apps/pages/pressure.py
from dash import register_page, html, dcc, Input, Output, callback
from textwrap import dedent

# Remove if not in your project
from apps.shared.ui import BLACK

register_page(__name__, path="/pressure", name="Water Pressure")

g = 9.81  # m/s^2

layout = html.Div(
    style={"width": "100%", "padding": "16px", "fontFamily": "Segoe UI, Inter, Arial", "color": BLACK},
    children=[
        html.H2("Total Pressure"),
        dcc.Markdown(
            "The **total pressure** at any point is the sum of the **static** and **velocity** pressure at that point.",
            mathjax=True, style={"marginBottom": "8px", "textAlign": "justify"},
        ),
        dcc.Markdown(r"$$p_t = p_s + p_v$$",
                     mathjax=True, style={"marginBottom": "16px", "textAlign": "left"}),

        dcc.Markdown(
            "Total pressure decreases in the direction of flow due to pipe and fitting losses. "
            "At the pump the total pressure is restored; therefore the pump pressure equals the **sum of system losses**, "
            "independent of the static head imposed by the head tank.",
            mathjax=True, style={"marginBottom": "24px", "textAlign": "justify"},
        ),

        html.H2("Static Pressure"),
        dcc.Markdown(
            "The **static pressure** at point A is the hydrostatic head from the tank level, "
            "plus the pump pressure, minus the losses to that point:",
            mathjax=True, style={"marginBottom": "8px", "textAlign": "justify"},
        ),
        dcc.Markdown(r"$$p_{sA} = (Z_H - Z_A)\,\rho\,g + p_p - p_L$$",
                     mathjax=True, style={"marginBottom": "8px", "textAlign": "left"}),

        # Use HTML subscripts/superscripts for bullet list (rendered with allow_html)
        dcc.Markdown(
            dedent("""
            **Where**

            - Z<sub>H</sub> — elevation of the water surface in the head tank (m)
            - Z<sub>A</sub> — elevation of point A (m)
            - ρ — fluid density (kg/m<sup>3</sup>)
            - g — gravitational acceleration (m/s<sup>2</sup>)
            - p<sub>p</sub> — pressure added by the pump (Pa)
            - p<sub>L</sub> — pressure losses in pipes and fittings to point A (Pa)
            """),
            mathjax=False,
            dangerously_allow_html=True,
            style={"marginBottom": "24px", "textAlign": "left"},
        ),

        # ----- Static Pressure Calculator -----
        html.H3("Static Pressure Calculator"),
        html.Div(
            style={
                "display": "grid",
                "gridTemplateColumns": "220px 160px 80px",
                "rowGap": "8px", "columnGap": "12px",
                "alignItems": "center", "maxWidth": "620px",
                "marginBottom": "12px",
            },
            children=[
                # Z_H
                dcc.Markdown(r"Tank level, $Z_H$", mathjax=True),
                dcc.Input(id="zh", type="number", value=10.0, step=0.1, style={"width": "160px"}),
                dcc.Markdown(r"$\mathrm{m}$", mathjax=True),

                # Z_A
                dcc.Markdown(r"Point elevation, $Z_A$", mathjax=True),
                dcc.Input(id="za", type="number", value=3.0, step=0.1, style={"width": "160px"}),
                dcc.Markdown(r"$\mathrm{m}$", mathjax=True),

                # rho
                dcc.Markdown(r"Fluid density, $\rho$", mathjax=True),
                dcc.Input(id="rho", type="number", value=1000.0, step=1, style={"width": "160px"}),
                dcc.Markdown(r"$\mathrm{kg\,m^{-3}}$", mathjax=True),

                # p_p
                dcc.Markdown(r"Pump pressure, $p_p$", mathjax=True),
                dcc.Input(id="pp", type="number", value=0.0, step=10, style={"width": "160px"}),
                dcc.Markdown(r"$\mathrm{Pa}$", mathjax=True),

                # p_L
                dcc.Markdown(r"Losses to A, $p_L$", mathjax=True),
                dcc.Input(id="pl", type="number", value=0.0, step=10, style={"width": "160px"}),
                dcc.Markdown(r"$\mathrm{Pa}$", mathjax=True),
            ],
        ),
        html.Div(id="static-output", style={"fontWeight": 600, "marginBottom": "24px"}),

        html.H2("Velocity Pressure"),
        dcc.Markdown("Velocity pressure is the kinetic energy term:",
                     mathjax=True, style={"marginBottom": "8px", "textAlign": "justify"}),
        dcc.Markdown(r"$$p_v = \tfrac{1}{2}\,\rho\,v^2$$",
                     mathjax=True, style={"marginBottom": "8px", "textAlign": "left"}),
        dcc.Markdown("For **water at 20 °C** (ρ ≈ 1000 kg/m³), the velocity pressure reduces to:",
                     mathjax=False, style={"marginBottom": "6px", "textAlign": "left"}),
        dcc.Markdown(r"$$p_v \approx 500\,v^2 \;(\mathrm{Pa})$$",
                     mathjax=True, style={"marginBottom": "8px", "textAlign": "left"}),
        dcc.Markdown("Example: change from 3.5 m/s to 3.0 m/s:",
                     mathjax=False, style={"marginBottom": "6px", "textAlign": "left"}),
        dcc.Markdown(r"$$\Delta p_v = 500\,(3.5^2 - 3.0^2) = 1625\ \mathrm{Pa} = 1.625\ \mathrm{kPa}$$",
                     mathjax=True, style={"marginBottom": "0px", "textAlign": "left"}),
    ],
)

@callback(
    Output("static-output", "children"),
    Input("zh", "value"),
    Input("za", "value"),
    Input("rho", "value"),
    Input("pp", "value"),
    Input("pl", "value"),
)
def calc_static(zh, za, rho, pp, pl):
    # Validate inputs
    if None in (zh, za, rho, pp, pl):
        return "Enter values to calculate static pressure."
    try:
        zh, za, rho, pp, pl = float(zh), float(za), float(rho), float(pp), float(pl)
    except (TypeError, ValueError):
        return "Invalid input."

    ps = (zh - za) * rho * g + pp - pl  # Pa
    head = ps / (rho * g) if rho > 0 else float("nan")  # m of fluid column
    return f"Static pressure at A: {ps:,.2f} Pa  ({ps/1000:,.3f} kPa)   •   Equivalent head: {head:,.3f} m"
