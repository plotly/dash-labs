from dash import Dash, html, dcc
import dash
import dash_labs as dl

app = Dash(__name__, plugins=[dl.plugins.pages])

dl.plugins.register_page("home", layout="We're home!", path="/")
dl.plugins.register_page(
    "very_important", layout="Don't miss it!", path="/important", order=0
)


app.layout = html.Div(
    [
        html.H1("App Frame"),
        html.Div(
            [
                html.Div(
                    dcc.Link(f"{page['name']} - {page['path']}", href=page["path"])
                )
                for page in dash.page_registry.values()
                if page["module"] != "pages.not_found_404"
            ]
        ),
        dl.plugins.page_container,
    ]
)


if __name__ == "__main__":
    app.run_server(debug=True)
