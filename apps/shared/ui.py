from dash import dcc, html

BRAND = "#38b43c"
BLACK = "#111"
WHITE = "#fff"
MUTED = "#5f6368"

def section_card(title, bullets, controls_row, result_id, extra_children=None):
    return html.Div(
        style={
            "backgroundColor": WHITE,
            "border": f"1px solid {BRAND}20",
            "borderLeft": f"6px solid {BRAND}",
            "borderRadius": "14px",
            "padding": "18px 18px 14px",
            "boxShadow": "0 6px 18px rgba(0,0,0,0.05)",
        },
        children=[
            html.H2(title, style={"margin":"0 0 8px 0", "fontSize":"22px", "color": BLACK}),
            html.Ul([html.Li(b, style={"marginBottom":"4px"}) for b in bullets],
                    style={"margin":"0 0 14px 18px", "color": MUTED}),
            html.Div(controls_row, style={
                "display":"flex","gap":"12px","flexWrap":"wrap",
                "alignItems":"center","marginBottom":"6px"
            }),
            html.Div(id=result_id, style={"fontWeight":"700","color":BLACK,"minHeight":"1.5em"}),
            (extra_children if extra_children is not None else html.Div())
        ]
    )

def input_box(_id, value, step=1, width="140px"):
    return dcc.Input(
        id=_id, type="number", value=value, step=step,
        style={"width":width,"padding":"10px 12px","borderRadius":"10px",
               "border":"1px solid #d9d9d9","outline":"none"}
    )

def dropdown(_id, options, value, width="200px"):
    return dcc.Dropdown(
        id=_id, options=[{"label":o, "value":o} for o in options], value=value,
        clearable=False,
        style={"width":width,"borderRadius":"10px","border":"1px solid #d9d9d9"}
    )
