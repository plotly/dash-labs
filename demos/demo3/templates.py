import dash
import dash_express as dx
import numpy as np
import dash_core_components as dcc
import plotly.express as px
from ddk_theme import theme

app = dash.Dash(__name__)
template = dx.templates.DdkSidebar(title="Dash Express App", theme=theme)
# template = dx.templates.DbcSidebar(title="Dash Express App")
# template = dx.templates.DccCard(title="Dash Express App")

@dx.parameterize(
    app,
    inputs=dict(
        fun=["sin", "cos", "exp"],
        figure_title="Initial Title",
        phase=(1, 10),
        amplitude=(1, 10)
    ),
    template=template,
    labels={
        "fun": "Function",
        "figure_title": "Figure Title",
        "phase": "Phase: {}",
        "amplitude": "Amplitude: {}"
    }
)
def callback_components(fun, figure_title, phase, amplitude):
    xs = np.linspace(-10, 10, 100)
    return template.Graph(figure=px.line(
        x=xs, y=getattr(np, fun)(xs + phase) * amplitude
    ).update_layout(title_text=figure_title))


app.layout = callback_components.layout

if __name__ == "__main__":
    app.run_server(debug=True, port=9003)
