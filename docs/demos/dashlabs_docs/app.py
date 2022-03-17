import dash
from dash import Dash, html
import dash_bootstrap_components as dbc
import dash_labs as dl


# syntax highlighting
light_hljs = "https://cdnjs.cloudflare.com/ajax/libs/highlight.js/11.4.0/styles/stackoverflow-light.min.css"
# dark_hljs = "https://cdnjs.cloudflare.com/ajax/libs/highlight.js/11.4.0/styles/stackoverflow-dark.min.css"

app = Dash(
    __name__,
    plugins=[dl.plugins.pages],
    external_stylesheets=[dbc.themes.SPACELAB, light_hljs],
    suppress_callback_exceptions=True,
)

topbar = html.H2(
    "Dash Labs Docs & Demo",
    className="p-4 bg-primary text-white ",
)

sidebar = dbc.Card(
    [
        dbc.NavLink(
            [
                html.Div("home", className="ms-2"),
            ],
            href=dash.page_registry["pages.home"]["path"],
            active="exact",
        ),
        html.H6("Multi-Page Apps", className="mt-2"),
        dbc.Nav(
            [
                dbc.NavLink(
                    [
                        html.Div(page["name"], className="ms-2"),
                    ],
                    href=page["path"],
                    active="exact",
                )
                for page in dash.page_registry.values()
                if page["module"].startswith("pages.multi_page_apps")
            ],
            vertical=True,
            pills=True,
        ),
        html.H6("Multi Page App Demo", className="mt-2"),
        dbc.Nav(
            [
                dbc.NavLink(
                    [
                        html.Div(page["name"], className="ms-2"),
                    ],
                    href=page["path"],
                    active="exact",
                )
                for page in dash.page_registry.values()
                if page["module"].startswith("pages.multi_page_demo")
            ],
            vertical=True,
            pills=True,
        ),
        html.H6("MarkdownAIO - Feature Preview", className="mt-2"),
        dbc.Nav(
            [
                dbc.NavLink(
                    [
                        html.Div(page["name"], className="ms-2"),
                    ],
                    href=page["path"],
                    active="exact",
                )
                for page in dash.page_registry.values()
                if page["module"].startswith("pages.MarkdownAIO")
            ],
            vertical=True,
            pills=True,
        ),
    ],
    className="overflow-auto sticky-top",
    style={"maxHeight": 600},
)

app.layout = dbc.Container(
    [
        dbc.Row(
            [
                topbar,
                dbc.Col(sidebar, width=4, lg=2),
                dbc.Col(dl.plugins.page_container, width=8, lg=10),
            ]
        ),
    ],
    fluid=True,
)


if __name__ == "__main__":
    app.run_server(debug=True)
