import dash
from dash import Dash, html
import dash_bootstrap_components as dbc
import dash_labs as dl

SIDEBAR_STYLE = {
    "position": "fixed",
    "top": 90,
    "left": 0,
    "bottom": 0,
    "width": "20rem",
    "padding": "2rem 1rem",
    "background-color": "#f8f9fa",
    "overflow": "auto",
}

# the styles for the main content position it to the right of the sidebar and
# add some padding.
CONTENT_STYLE = {
    "margin-left": "20rem",
    "margin-right": "2rem",
    "padding": "2rem 2rem",
}


# syntax highlighting
light_hljs = "https://cdnjs.cloudflare.com/ajax/libs/highlight.js/11.4.0/styles/stackoverflow-light.min.css"
dark_hljs = "https://cdnjs.cloudflare.com/ajax/libs/highlight.js/11.4.0/styles/stackoverflow-dark.min.css"

app = Dash(
    __name__,
    plugins=[dl.plugins.pages],
    external_stylesheets=[dbc.themes.SPACELAB, light_hljs],
    suppress_callback_exceptions=True,
)


topbar = html.H2(
    "Dash Labs Docs & Demo", className="p-4 bg-primary text-white sticky-top"
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
        html.H6("Dashdown", className="mt-2"),
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
                if page["module"].startswith("pages.dashdown")
            ],
            vertical=True,
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
                if page["path"].startswith("/multi-page")
            ],
            vertical=True,
        ),
    ],
    className="overflow-auto",
    style=SIDEBAR_STYLE,
)

app.layout = html.Div(
    [topbar, sidebar, html.Div(dl.plugins.page_container, style=CONTENT_STYLE)]
)


if __name__ == "__main__":
    app.run_server(debug=True)
