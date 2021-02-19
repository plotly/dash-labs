import dash
import dash_express as dx
from dash.dependencies import Input, InputComponent

import numpy as np
import dash_core_components as dcc
import plotly.express as px

app = dash.Dash(__name__, plugins=[dx.Plugin()])

@app.callback(dict(
        fun=InputComponent(dcc.Dropdown(["sin", "cos", "exp"]), label="Function"),
        figure_title=InputComponent(dcc.Input("Initial Title"), label="Figure Title"),
        phase=InputComponent(dcc.Slider((1, 10)), label="Phase"),
        amplitude=InputComponent(dcc.Slider((1, 10)), label="Amplitude"),
))
def greet(fun, figure_title, phase, amplitude):
    xs = np.linspace(-10, 10, 100)
    return dcc.Graph(figure=px.line(
        x=xs, y=getattr(np, fun)(xs + phase) * amplitude
    ).update_layout(title_text=figure_title))

app.layout = greet.layout(app)

if __name__ == "__main__":
    app.run_server(debug=True)
