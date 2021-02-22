import dash
import dash_express as dx
import numpy as np
import dash_core_components as dcc
import plotly.express as px

app = dash.Dash(__name__, plugins=[dx.Plugin()])
tp = dx.templates.FlatDiv()

@app.callback(
    args=dict(
        fun=dx.Input(dcc.Dropdown(
            options=[{"value": v, "label": v} for v in ["sin", "cos", "exp"]],
            value="sin"
        )),
        figure_title=dx.Input(dcc.Input(value="Initial Title")),
        phase=dx.Input(dcc.Slider(min=1, max=10, value=4)),
        amplitude=dx.Input(dcc.Slider(min=1, max=10, value=3)),
    ),
    template=tp,
)
def greet(fun, figure_title, phase, amplitude):
    print(fun, figure_title, phase, amplitude)
    xs = np.linspace(-10, 10, 100)
    return dcc.Graph(figure=px.line(
        x=xs, y=getattr(np, fun)(xs + phase) * amplitude
    ).update_layout(title_text=figure_title))


app.layout = greet.layout(app)

if __name__ == "__main__":
    app.run_server(debug=True)
