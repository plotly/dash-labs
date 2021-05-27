import time
import plotly.express as px
import dash
import dash_core_components as dcc
import dash_html_components as html
import dash_labs as dl
from celery import Celery

celery_app = Celery(__name__, backend='rpc://', broker='pyamqp://')


app = dash.Dash(__name__, plugins=[
    dl.plugins.FlexibleCallbacks(), dl.plugins.HiddenComponents(), dl.plugins.LongCallback2(celery_app)
])

app.layout = html.Div([
    html.Div([
        html.P(id="paragraph_id", children=["Button not clicked"]),
        html.Progress(id="progress_bar"),
    ]),
    html.Button(id='button_id', children="Run Job!"),
    html.Button(id='cancel_button_id', children="Cancel Running Job!"),
])


@app.long_callback(
    output=dl.Output("paragraph_id", "children"),
    args=dl.Input("button_id", "n_clicks"),
    running=[
        (dl.Output("button_id", "disabled"), True, False),
        (dl.Output("cancel_button_id", "disabled"), False, True),
        (dl.Output("paragraph_id", "style"), {"visibility": "hidden"}, {"visibility": "visible"}),
        (dl.Output("progress_bar", "style"), {"visibility": "visible"}, {"visibility": "hidden"}),
    ],
    cancel=[dl.Input("cancel_button_id", "n_clicks")],
    progress=dl.Output("progress_bar", ("value", "max")),
)
def callback(set_progress, n_clicks):
    total = 10
    for i in range(total):
        time.sleep(0.5)
        set_progress(str(i + 1), str(total))
    # Set progress back to indeterminate state for next time
    set_progress(None, None)
    return [f"Clicked {n_clicks} times"]


if __name__ == "__main__":
    app.run_server(debug=True)
