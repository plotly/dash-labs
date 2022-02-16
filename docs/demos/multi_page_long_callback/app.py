import dash
import dash_labs as dl

from dash import html, dcc
from dash.long_callback import DiskcacheLongCallbackManager
from dash.dependencies import Input, Output

## Diskcache
import diskcache

cache = diskcache.Cache("./cache")
long_callback_manager = DiskcacheLongCallbackManager(cache)
import time

app = dash.Dash(__name__, plugins=[dl.plugins.pages])

navbar = html.Div(
    [
        html.Div(dcc.Link(page["name"], href=page["path"]))
        for page in dash.page_registry.values()
    ],
    style={"backgroundColor": "whitesmoke", "padding": 10},
)

app.layout = html.Div(
    [navbar, html.Hr(), dl.plugins.page_container],
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
