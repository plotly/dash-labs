import dash
import dash_labs as dl
import dash_bootstrap_components as dbc
import numpy as np
import plotly.express as px

app = dash.Dash(__name__, plugins=[dl.plugins.FlexibleCallbacks()])

tpl = dl.templates.DbcSidebar(app, title="Dynamic Label Plugin", figure_template=True)
phase_plugin = dl.component_plugins.DynamicLabelPlugin(
    tpl.slider_input(1, 10, value=4, label="Phase: {:.1f}", tooltip=False), template=tpl
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
    fig = px.line(x=xs, y=getattr(np, fun)(xs + phase), title="Function Value")

    return [fig, phase_plugin.get_output_values(phase_inputs)]


app.layout = dbc.Container(fluid=True, children=tpl.children)

if __name__ == "__main__":
    app.run_server(debug=True)
