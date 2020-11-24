import dash
import dash_express as dx
import numpy as np
import dash_design_kit as ddk
from ddk_theme import theme
import plotly.express as px


app = dash.Dash(__name__)


@dx.interact(
    dx.layouts.ddk.DdkSidebarLayout(
        app, title="DDK Dash Express App", theme=theme, show_editor=True,
    ),
    labels={
        "fun": "Function",
        "figure_title": "Figure Title",
        "phase": "Phase: {value}",
        "amplitude": "Amplitude: {value}"
    }
)
def greet(
        fun=["sin", "cos", "exp"],
        figure_title="",
        phase=(1, 10),
        amplitude=(1, 10),
):
    xs = np.linspace(-10, 10, 100)
    return ddk.Graph(figure=px.line(
        x=xs, y=getattr(np, fun)(xs + phase) * amplitude
    ).update_layout(title_text=figure_title))


app.layout = greet.layout()

if __name__ == "__main__":
    app.run_server(debug=True, port=9004)
