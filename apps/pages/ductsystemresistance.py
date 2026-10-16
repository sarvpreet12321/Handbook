# apps/pages/ductsystem_resistance.py
from dash import register_page, html, dcc
from apps.shared.ui import BRAND, MUTED, BLACK

register_page(__name__, path="/ductsystemresistance", name="Duct System Resistance")

layout = html.Div(
    style={"width": "100%", "padding": "16px", "fontFamily": "Segoe UI, Inter, Arial", "color": BLACK},
    children=[
        dcc.Markdown(
            """
            The total system resistance loss in a duct system is a combination of friction and dynamic losses.
            """,
            mathjax=True, style={"marginBottom": "12px", "textAlign": "justify"},
        ),
        dcc.Markdown(
            """
            In straight ducts the dynamic loss is insignificant and the total loss is assumed to be all friction.  
            With uniform air flow the drop in pressure in the direction of flow is caused by surface friction between the
            air stream and the duct surface. This value is found by reference to duct friction charts, or alternatively a
            value may be assumed, e.g. **1.00 Pa/m** for the Constant Pressure Gradient method of duct sizing.
            """,
            mathjax=True, style={"marginBottom": "12px", "textAlign": "justify"},
        ),
        dcc.Markdown(
            """
            Whenever air flow separates from the duct wall a greater loss in total pressure takes place than would occur
            with non-separated flow. The amount of this loss in excess of straight duct friction loss is termed *dynamic loss*.  
            Dynamic losses vary theoretically as the square of the characteristic velocity of the airstream and are expressed as a
            function of velocity pressure.
            """,
            mathjax=True, style={"marginBottom": "12px", "textAlign": "justify"},
        ),
        dcc.Markdown(
            """
            For duct fittings both dynamic and friction losses are significant.  
            Data for fittings are given in terms of total loss, expressed as a loss coefficient $K_T$. Values of $K_T$ are given in the following tables.
            """,
            mathjax=True, style={"marginBottom": "18px", "textAlign": "justify"},
        ),

        dcc.Markdown("### Total pressure loss", style={"margin": "6px 0"}),

        dcc.Markdown(
            r"""
        Total pressure loss is given by:

        $$
        P_T = K_T P_v
        $$

        or

        $$
        P_T = K_T \left(P_{v1} - P_{v2}\right)
        $$

        where:

        - $P_T$ = total pressure loss (Pa)  
        - $K_T$ = loss coefficient (obtained from the following tables)  
        - $P_v$ = velocity pressure
            """,
            mathjax=True,
            style={"marginBottom": "20px"},
        ),

        dcc.Markdown("### Velocity pressure", style={"margin": "6px 0"}),

        dcc.Markdown(
            r"""
        Velocity pressure is given by:

        $$
        P_v = 0.50 \rho V^2
        $$

        For standard air at $20^{\circ}\mathrm{C}$ ($\rho \approx 1.2\ \mathrm{kg/m^3}$), this is commonly taken as:

        $$
        P_v \approx 0.60 V^2 \ \text{Pa}
        $$

        where:

        - $V$ = velocity of the air stream (m/s)  
        - $\rho$ = density of air (kg/m³)
            """,
            mathjax=True,
            style={"marginBottom": "20px"},
        ),

        dcc.Markdown(
            "Values of velocity pressure are obtained from the following table.",
            mathjax=True,
            style={"marginBottom": "12px"},
        ),

    ],
)
