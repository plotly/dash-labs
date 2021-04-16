import time
import plotly.express as px
import dash
import dash_core_components as dcc
import dash_html_components as html
import dash_labs as dl
from docs.demos.progress_bar_idea.background_callback_object import BackgroundCallback
from flask_caching import Cache

app = dash.Dash(__name__, plugins=[dl.plugins.FlexibleCallbacks(), dl.plugins.HiddenComponents()])
cache = Cache(app.server, config={"CACHE_TYPE": "filesystem", "CACHE_DIR": "./cache"})

background_callback = BackgroundCallback(app, cache, 1000)

app.layout = html.Div([
    html.Div(
        background_callback.Loading(html.P(id="paragraph_id", children="Button not clicked", loading_state=dict(
            is_loading=True,
            component_name="paragraph_id",
            prop_name="children",
        )))
        # dcc.Loading(
        #
        # )
    ),
    html.Button(id='button_id', children="Run Job!"),
    html.Button(id='cancel_button_id', children="Cancel Running Job!"),
])

@background_callback.callback(
    output=dl.Output("paragraph_id", "children"),
    args=dl.Input("button_id", "n_clicks"),
    disable=[dl.Output("button_id", "disabled")],
    enable=[dl.Output("cancel_button_id", "disabled")],
    cancel=[dl.Input("cancel_button_id", "n_clicks")]
)
def callback(n_clicks):
    time.sleep(2)
    return f"Clicked {n_clicks} times"


if __name__ == "__main__":
    app.run_server(debug=True)
