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
        ), label="Function"),
        phase=phase_plugin.args,
    ),
    output=[tp.graph(), phase_plugin.output],
    template=tp,
)
def callback(fun, phase):
    xs = np.linspace(-10, 10, 100)
    fig = px.line(
        x=xs, y=getattr(np, fun)(xs + phase)
    ).update_layout()

    return [fig, phase_plugin.build(phase)]


app.layout = tp.layout(app)

if __name__ == "__main__":
    app.run_server(debug=True)
