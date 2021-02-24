import dash
import dash_express as dx
import numpy as np
import dash_core_components as dcc
import plotly.express as px

app = dash.Dash(__name__, plugins=[dx.Plugin()])
tp = dx.templates.FlatDiv()

@app.callback(
    args=dict(
        fun=tp.dropdown(["sin", "cos", "exp"], label="Function", kind=dx.State),
        figure_title=tp.input("Initial Title", label="Figure Title", kind=dx.State),
        phase=tp.slider(1, 10, label="Phase", kind=dx.State),
        amplitude=tp.slider(1, 10, value=3, label="Amplitude", kind=dx.State),
        n_clicks=tp.button("Update", label=None)
    ),
    template=tp
)
def greet(fun, figure_title, phase, amplitude, n_clicks):
    print(fun, figure_title, phase, amplitude)
    xs = np.linspace(-10, 10, 100)
    return dcc.Graph(figure=px.line(
        x=xs, y=getattr(np, fun)(xs + phase) * amplitude
    ).update_layout(title_text=figure_title))


app.layout = tp.layout(app)

if __name__ == "__main__":
    app.run_server(debug=True)
