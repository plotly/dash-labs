import time
import dash
import dash_html_components as html
import dash_labs as dl
from dash_labs.plugins import CeleryCallbackManager, DiskcacheCachingCallbackManager

# ## Celery on RabbitMQ
# from celery import Celery
# celery_app = Celery(__name__, backend='rpc://', broker='pyamqp://')
# long_callback_manager = CeleryCallbackManager(celery_app)

# ## Celery on Redis
# from celery import Celery
#
# celery_app = Celery(
#     __name__, broker="redis://localhost:6379/0", backend="redis://localhost:6379/1"
# )
# long_callback_manager = CeleryCallbackManager(celery_app, cache_by=[lambda: True])

# # ## FlaskCaching
# from flask_caching import Cache
#
# flask_cache = Cache(config={"CACHE_TYPE": "filesystem", "CACHE_DIR": "./cache"})
# long_callback_manager = FlaskCachingCallbackManager(
#     flask_cache, clear_cache=True, cache_by=[lambda: True]
# )

## Diskcache
import diskcache

cache = diskcache.Cache("./cache")
long_callback_manager = DiskcacheCachingCallbackManager(cache)

app = dash.Dash(
    __name__,
    plugins=[
        dl.plugins.FlexibleCallbacks(),
        dl.plugins.HiddenComponents(),
        dl.plugins.LongCallback(long_callback_manager),
    ],
)

app.layout = html.Div(
    [
        html.Div([html.P(id="paragraph_id", children=["Button not clicked"])]),
        html.Button(id="button_id", children="Run Job!"),
    ]
)


@app.long_callback(
    output=dl.Output("paragraph_id", "children"),
    args=dl.Input("button_id", "n_clicks"),
)
def callback(n_clicks):
    time.sleep(2.0)
    return [f"Clicked {n_clicks} times"]


if __name__ == "__main__":
    app.run_server(debug=True)
