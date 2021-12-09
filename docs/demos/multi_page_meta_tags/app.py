from dash import Dash, html, dcc
import dash
import dash_labs as dl

app = Dash(__name__, plugins=[dl.plugins.pages])


app.layout = html.Div(
    [
        html.H1("App Frame"),
        html.Div(
            [
                html.Div(
                    [
                        html.Img(
                            src=app.get_asset_url(page["image"]),
                            height="40px",
                            width="60px",
                        ),
                        dcc.Link(f"{page['name']} - {page['path']}", href=page["path"]),
                    ],
                    style={"margin": 20},
                )
                for page in dash.page_registry.values()
            ]
        ),
        dl.plugins.page_container,
    ]
)


if __name__ == "__main__":
    app.run_server(debug=True)
