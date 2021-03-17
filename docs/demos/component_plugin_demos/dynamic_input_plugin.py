import dash
import dash_labs as dl
import numpy as np
import plotly.express as px

app = dash.Dash(__name__, plugins=[dl.Plugin()])

tpl = dl.templates.DbcSidebar(title="Dynamic Label Plugin")
phase_plugin = dl.component_plugins.DynamicInputPlugin(
    tpl.slider_input(1, 10, value=4, label="Phase: {:.1f}"), template=tpl
)


@app.callback(
    args=dict(
        fun=tpl.dropdown_input(["sin", "cos", "exp"], label="Function"),
        phase_inputs=phase_plugin.args,
    ),
    output=[tpl.graph_output(), phase_plugin.output],
    template=tpl,
)
def callback(fun, phase_inputs):
    phase = phase_plugin.get_value(phase_inputs)
    xs = np.linspace(-10, 10, 100)
    fig = px.line(x=xs, y=getattr(np, fun)(xs + phase)).update_layout()

    return [fig, phase_plugin.get_output_values(phase_inputs)]


app.layout = tpl.layout(app)

if __name__ == "__main__":
    app.run_server(debug=True)
