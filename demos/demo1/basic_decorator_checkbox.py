import dash
import dash_express as dx
import numpy as np
import dash_core_components as dcc
import plotly.express as px


app = dash.Dash(__name__)

@dx.parameterize(
    app,
    inputs=dict(
        fun=["sin", "cos", "exp"], figure_title="Initial Title",
        phase=(1, 10), amplitude=(1, 10), uppercase=False,
    ),
)
def greet(fun, figure_title, phase, amplitude, uppercase):
    xs = np.linspace(-10, 10, 100)
    title = figure_title
    if uppercase:
        title = title.upper()
    return dcc.Graph(figure=px.line(
        x=xs, y=getattr(np, fun)(xs + phase) * amplitude
    ).update_layout(title_text=title))

app.layout = greet.layout(app)

if __name__ == "__main__":
    app.run_server(debug=True, port=9102)
