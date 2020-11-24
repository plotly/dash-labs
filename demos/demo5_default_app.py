import dash
import dash_express as dx
import numpy as np
import dash_core_components as dcc
import plotly.express as px


@dx.interact(
    dx.layouts.dbc.DbcSidebarLayout(title="Dash Express App"),
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
    return dcc.Graph(figure=px.line(
        x=xs, y=getattr(np, fun)(xs + phase) * amplitude
    ).update_layout(title_text=figure_title))

if __name__ == "__main__":
    greet.run_server(debug=True, port=9005)
