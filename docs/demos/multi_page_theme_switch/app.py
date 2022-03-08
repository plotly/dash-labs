import dash
import dash_labs as dl
import dash_bootstrap_components as dbc
from dash_bootstrap_templates import ThemeSwitchAIO
template_theme1 = "flatly"
template_theme2 = "darkly"
url_theme1 = dbc.themes.FLATLY
url_theme2 = dbc.themes.DARKLY

dbc_css = (
    "https://cdn.jsdelivr.net/gh/AnnMarieW/dash-bootstrap-templates/dbc.min.css"
)
app = dash.Dash(
    __name__, plugins=[dl.plugins.pages], external_stylesheets=[dbc.themes.BOOTSTRAP, dbc_css]
)

navbar = dbc.NavbarSimple(
    dbc.DropdownMenu(
        [
            dbc.DropdownMenuItem(page["name"], href=page["path"])
            for page in dash.page_registry.values()
            if page["module"] != "pages.not_found_404"
        ],
        nav=True,
        label="More Pages",
    ),
    brand="Multi Page App Plugin Demo",
    color="primary",
    dark=True,
    className="mb-2",
)
theme_sw = ThemeSwitchAIO(aio_id="theme", themes=[url_theme1, url_theme2],)
app.layout = dbc.Container(
    [navbar,theme_sw, dl.plugins.page_container],
    fluid=True,
    className="dbc"
)

if __name__ == "__main__":
    app.run_server(debug=True)
