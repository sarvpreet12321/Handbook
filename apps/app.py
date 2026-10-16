from dash import Dash, html, page_container

app = Dash(
    __name__,
    use_pages=True,
    requests_pathname_prefix="/apps/",
    routes_pathname_prefix="/apps/",
    suppress_callback_exceptions=True,
)

app.title = "AWP Tools"

app.layout = html.Div(
    # full-width root
    style={"width": "100%", "margin": "0", "padding": "0"},
    children=[
        # right-anchored content column
        html.Div(
            children=[
                page_container,
                html.Hr(),
                html.Div("© AWP", style={"fontSize": "12px", "color": "#666", "textAlign": "center"}),
            ],
            style={
                # keep content on the right
                "marginLeft": "auto",
                "marginRight": "0",
                # choose a comfortable max width but still responsive
                "maxWidth": "min(1400px, 98vw)",
                "padding": "20px",
            },
        ),
    ],
)

if __name__ == "__main__":
    app.run(port=8050, debug=False)
