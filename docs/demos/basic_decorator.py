import dash
import dash_express as dx
import numpy as np
import dash_core_components as dcc
import plotly.express as px

app = dash.Dash(__name__, plugins=[dx.Plugin()])
tpl = dx.templates.dbc.DbcSidebar(title="Sample App")

@app.callback(
    args=dict(
        fun=tpl.dropdown(["sin", "cos", "exp"], label="Function"),
        figure_title=tpl.input("Initial Title", label="Figure Title"),
        phase=tpl.slider(1, 10, label="Phase"),
        amplitude=tpl.slider(1, 10, value=3, label="Amplitude"),
    ),
    template=tpl
)
def greet(fun, figure_title, phase, amplitude):
    print(fun, figure_title, phase, amplitude)
    xs = np.linspace(-10, 10, 100)
    return dcc.Graph(figure=px.line(
        x=xs, y=getattr(np, fun)(xs + phase) * amplitude
    ).update_layout(title_text=figure_title))


app.layout = tpl.layout(app)

if __name__ == "__main__":
    app.run_server(debug=True)
