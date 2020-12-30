import dash
import dash_express as dx
import numpy as np
import dash_core_components as dcc
import dash_html_components as html
import plotly.express as px

app = dash.Dash(__name__)

@dx.parameterize(
    app,
    inputs=dict(
        fun=dx.state(["sin", "cos", "exp"]),
        figure_title=dx.state("Initial Title"),
        phase=dx.state((1, 10)),
        amplitude=dx.state((1, 10)),
        n_clicks=(html.Button("Update"), "n_clicks")
    ),
    labels=dict(
        fun="Function",
        figure_title="Figure Title",
        phase="Phase: {:.2f}",
        amplitude="Amplitude: {:.2f}",
        n_clicks=None,
    ),
    optional=["fun", "figure_title"],
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
    app.run_server(debug=True, port=9102)
