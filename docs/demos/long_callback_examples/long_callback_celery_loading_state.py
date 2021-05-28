import time
import plotly.express as px
import dash
import dash_core_components as dcc
import dash_html_components as html
import dash_labs as dl
from celery import Celery

from flask_caching import Cache

from dash_labs.plugins import FlaskCachingCallbackManager, CeleryCallbackManager

# celery_app = Celery(__name__, backend='rpc://', broker='pyamqp://')
# long_callback_manager = CeleryCallbackManager(celery_app)

flask_cache = Cache(config={"CACHE_TYPE": "filesystem", "CACHE_DIR": "./cache"})
long_callback_manager = FlaskCachingCallbackManager(flask_cache)

app = dash.Dash(__name__, plugins=[
    dl.plugins.FlexibleCallbacks(),
    dl.plugins.HiddenComponents(),
    dl.plugins.LongCallback(long_callback_manager)
])


app.layout = html.Div([
    html.Div([
        dcc.Loading(id="loading_component", children=[
            html.P(id="paragraph_id", children=["Button not clicked"])
        ])
    ]),
    html.Button(id='button_id', children="Run Job!"),
    html.Button(id='cancel_button_id', children="Cancel Running Job!"),
])

@app.long_callback(
    output=dl.Output("paragraph_id", "children"),
    args=dl.Input("button_id", "n_clicks"),
    running=[
        (dl.Output("loading_component", "in_progress"), True, False),
        (dl.Output("button_id", "disabled"), True, False),
        (dl.Output("cancel_button_id", "disabled"), False, True),
    ],
    cancel=[dl.Input("cancel_button_id", "n_clicks")],
)
def callback(n_clicks):
    time.sleep(5.0)
    return [f"Clicked {n_clicks} times"]


if __name__ == "__main__":
    app.run_server(debug=True)