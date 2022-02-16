import dash
import dash_labs as dl
import dash_bootstrap_components as dbc

from dash import html
from dash.long_callback import DiskcacheLongCallbackManager
from dash.dependencies import Input, Output

## Diskcache
import diskcache

cache = diskcache.Cache("./cache")
long_callback_manager = DiskcacheLongCallbackManager(cache)
import time

app = dash.Dash(
    __name__, plugins=[dl.plugins.pages], external_stylesheets=[dbc.themes.BOOTSTRAP]
)

navbar = dbc.NavbarSimple(
    dbc.DropdownMenu(
        [
            dbc.DropdownMenuItem(page["name"], href=page["path"])
            for page in dash.page_registry.values()
        ],
        nav=True,
        label="More Pages",
    ),
    brand="Multi Page App Plugin Demo",
    color="primary",
    dark=True,
    className="mb-2",
)

app.layout = dbc.Container(
    [navbar, dl.plugins.page_container],
    fluid=True,
)


@app.long_callback(
    output=Output("paragraph_id", "children"),
    inputs=Input("button_id", "n_clicks"),
    manager=long_callback_manager,
    prevent_initial_call=True,
)
def callback(n_clicks):
    time.sleep(2.0)
    return [f"Clicked {n_clicks} times"]


if __name__ == "__main__":
    app.run_server(debug=True)
