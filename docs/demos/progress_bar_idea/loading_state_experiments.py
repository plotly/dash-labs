from dash.exceptions import PreventUpdate

import dash_labs as dl
import dash
import dash_core_components as dcc
import dash_html_components as html

import time

app = dash.Dash(__name__, plugins=[dl.plugins.FlexibleCallbacks()])


app.layout = html.Div([
    # dcc.Loading(id="loading-state", children=[
    #     html.P(id="paragraph")
    # ]),
    html.Div(
    # html.Progress(id="progress", max=str(10), value=str(3), children=[
        html.Div(
        html.P(id="paragraph", children="Some long long long Some long long long Some long long long Some long long long Some long long long Some long long long Some long long long Some long long long")
        )
    # ]),
    ),
    html.Button(id="button", children="Click Here")
    # dcc.Interval(id="interval", disabled=False, interval=500)
])


@app.callback(
    [
     dl.Output("paragraph", "children"),
     # dl.Output("progress", "value"),
     # dl.Output("progress", "max"),
     # dl.Output("interval", "disabled")
    ],
    # dl.Input("interval", "n_intervals"),
    dl.Input("button", "n_clicks"),
)
def update(n_intervals):
    # print(loading)
    # time.sleep(2)
    print(n_intervals)
    # if n_intervals and n_intervals % 2 == 0:
    #     raise PreventUpdate
    # return (f"{n_intervals=}", str(n_intervals), False)
    # return (f"{n_intervals=}", str(n_intervals), "20")
    return [f"{n_intervals=}"]

if __name__ == "__main__":
    app.run_server(debug=True)
