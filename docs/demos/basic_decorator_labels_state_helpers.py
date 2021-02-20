import dash
import dash_express as dx
import numpy as np
import dash_core_components as dcc
import dash_html_components as html
import plotly.express as px

app = dash.Dash(__name__, plugins=[dx.Plugin()])
tp = dx.templates.dbc.DbcSidebar()
@app.callback(
    args=dict(
        fun=tp.dropdown(["sin", "cos", "exp"], label="Function", kind=dx.State),
        figure_title=tp.input("Initial Title", label="Figure Title", kind=dx.State),
        phase=tp.slider(1, 10, label="Phase", kind=dx.State),
        amplitude=tp.slider(1, 10, value=3, label="Amplitude", kind=dx.State),
        n_clicks=tp.button("Update", label=None, kind=dx.Input),
    ),
    template=tp
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
