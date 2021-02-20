import dash
import dash_express as dx
import numpy as np
import dash_core_components as dcc
import plotly.express as px

app = dash.Dash(__name__, plugins=[dx.Plugin()])

tp = dx.templates.DbcSidebar(title="Dynamic Label Plugin")
phase_plugin = dx.component_plugins.DynamicInputPlugin(
    tp.slider(1, 10, value=4, label="Phase: {}"), template=tp
)

@app.callback(
    args=dict(
        fun=dx.Input(dcc.Dropdown(
            options=[{"value": v, "label": v} for v in ["sin", "cos", "exp"]],
            value="sin"
        )),
        figure_title=dx.Input(dcc.Input(value="Initial Title")),
        phase_inputs=phase_plugin.inputs,
        amplitude=tp.slider(1, 10, value=4, label="Amplitude"),
    ),
    output=[tp.graph(), phase_plugin.output],
    template=tp,
)
def greet(fun, figure_title, phase_inputs, amplitude):
    print(fun, figure_title, phase_inputs, amplitude)
    phase = phase_plugin.get_value(phase_inputs)

    xs = np.linspace(-10, 10, 100)
    fig = px.line(
        x=xs, y=getattr(np, fun)(xs + phase) * amplitude
    ).update_layout(title_text=figure_title)

    return [fig, phase_plugin.build(phase_inputs)]


app.layout = greet.layout(app)

if __name__ == "__main__":
    app.run_server(debug=True)
