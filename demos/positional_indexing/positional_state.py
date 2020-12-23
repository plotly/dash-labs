import dash
from dash.dependencies import State, Input

import dash_express as dx
import numpy as np
import plotly.express as px
import dash_core_components as dcc
app = dash.Dash(__name__)
# template = dx.templates.DbcSidebar(title="Dash Express App")
template = dx.templates.DdkSidebar(title="Dash Express App")
# template = dx.templates.DccCard(title="Dash Express App")
# template = dx.templates.FlatDiv()


outside_input = dcc.Input(id=dx.build_component_id("intput", "outside-input"))

@dx.parameterize(
    app,
    inputs=[["sin", "cos", "exp"], "Initial Title"],
    state=[(1, 10), (1, 20), Input(outside_input.id, "value")],
    template=template,
    labels={
        0: "Function",
        1: "Figure Title",
        2: "Phase: {}",
        3: "Amplitude: {}"
    },
    optional=["fun", "phase"],
)
def callback_components(fun, figure_title, phase, amplitude, outside_state):
    print("fun", fun, "figure_title", figure_title, "phase", phase, "amplitude", amplitude, "outside_state", outside_state)

    xs = np.linspace(-10, 10, 100)
    if fun is None:
        np_fn = lambda a: a
    else:
        np_fn = getattr(np, fun)

    if phase is None:
        phase = 0

    # Let parameterize infer output component
    x = xs
    y = np_fn(xs + phase) * amplitude
    return template.Graph(
        figure=px.line(x=x, y=y).update_layout(title_text=figure_title)
    )

print(template.output_containers)
layout = callback_components.layout
layout.children.insert(0, outside_input)
app.layout = layout

if __name__ == "__main__":
    app.run_server(debug=True, port=9209)
