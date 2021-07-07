import time
import dash
import dash_html_components as html
import dash_core_components as dcc
import dash_labs as dl
from dash_labs.plugins import DiskcacheCachingCallbackManager, CeleryCallbackManager
import plotly.graph_objects as go

# ## Celery on RabbitMQ
# from celery import Celery
# celery_app = Celery(__name__, backend='rpc://', broker='pyamqp://')
# long_callback_manager = CeleryCallbackManager(celery_app)

# ## Celery on Redis
# from celery import Celery
# celery_app = Celery(
#     __name__, broker='redis://localhost:6379/0', backend='redis://localhost:6379/1'
# )
# long_callback_manager = CeleryCallbackManager(celery_app)

## Diskcache
import diskcache

cache = diskcache.Cache("./cache")
long_callback_manager = DiskcacheCachingCallbackManager(cache)


def make_progress_graph(progress, total):
    progress_graph = (
        go.Figure(data=[go.Bar(x=[progress])])
        .update_xaxes(range=[0, total])
        .update_yaxes(
            showticklabels=False,
        )
        .update_layout(height=100, margin=dict(t=20, b=40))
    )
    return progress_graph


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
        html.Div(
            [
                html.P(id="paragraph_id", children=["Button not clicked"]),
                dcc.Graph(id="progress_bar_graph", figure=make_progress_graph(0, 10)),
            ]
        ),
        html.Button(id="button_id", children="Run Job!"),
        html.Button(id="cancel_button_id", children="Cancel Running Job!"),
    ]
)


@app.long_callback(
    output=dl.Output("paragraph_id", "children"),
    args=dl.Input("button_id", "n_clicks"),
    running=[
        (dl.Output("button_id", "disabled"), True, False),
        (dl.Output("cancel_button_id", "disabled"), False, True),
        (
            dl.Output("paragraph_id", "style"),
            {"visibility": "hidden"},
            {"visibility": "visible"},
        ),
        (
            dl.Output("progress_bar_graph", "style"),
            {"visibility": "visible"},
            {"visibility": "hidden"},
        ),
    ],
    cancel=[dl.Input("cancel_button_id", "n_clicks")],
    progress=dl.Output("progress_bar_graph", "figure"),
    progress_default=make_progress_graph(0, 10),
    interval=1000,
)
def callback(set_progress, n_clicks):
    total = 10
    for i in range(total):
        time.sleep(0.5)
        set_progress(make_progress_graph(i, 10))

    return [f"Clicked {n_clicks} times"]


if __name__ == "__main__":
    app.run_server(debug=True)
