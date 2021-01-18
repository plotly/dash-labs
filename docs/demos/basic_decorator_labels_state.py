import dash
import dash_express as dx
import numpy as np
import dash_core_components as dcc
import dash_html_components as html
import plotly.express as px

app = dash.Dash(__name__)

@dx.callback(
    app,
    inputs=dict(
        fun=dx.arg(["sin", "cos", "exp"], label="Function", kind="state"),
        figure_title=dx.arg("Initial Title", label="Figure Title", kind="state"),
        phase=dx.arg((1, 10), label="Phase", kind="state"),
        amplitude=dx.arg((1, 10), label="Amplitude", kind="state"),
        n_clicks=dx.arg(html.Button("Update").props["n_clicks"], kind="input")
    ),
)
def greet(fun, figure_title, phase, amplitude, n_clicks):
    xs = np.linspace(-10, 10, 100)
    if fun is None:
        ys = xs
    else:
        ys = getattr(np, fun)(xs + phase) * amplitude

    figure_title = "No Title" if figure_title is None else figure_title
    return dcc.Graph(figure=px.line(
        x=xs, y=ys
    ).update_layout(title_text=figure_title))


app.layout = greet.layout(app)

if __name__ == "__main__":
    app.run_server(debug=True)
