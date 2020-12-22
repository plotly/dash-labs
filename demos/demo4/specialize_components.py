import dash
import dash_express as dx
import numpy as np
import dash_core_components as dcc
import dash_bootstrap_components as dbc
import plotly.express as px


app = dash.Dash(__name__)
template = dx.templates.DbcSidebar(title="Dash Express App")


# Function to parameterize
@dx.parameterize(
    app,
    input=dict(
        fun=["sin", "cos", "exp"],

        # Style input using bootstrap classes
        figure_title=dbc.Input(type="text", value="", className="bg-primary text-white"),

        # Explicitly specify component property. Default is "value"
        phase=(dcc.Slider(min=1, max=10, value=5, step=1), "value"),

        # Dropdown instead of default slider
        amplitude=dbc.Select(
            options=[{"label": i, "value": i} for i in range(1, 10)],
            value=4,
        ),
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
        x=xs, y=getattr(np, fun)(xs + phase) * float(amplitude)
    ).update_layout(title_text=figure_title))


app.layout = callback_components.layout

if __name__ == "__main__":
    app.run_server(debug=True, port=9006)
