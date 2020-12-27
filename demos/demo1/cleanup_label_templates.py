import dash
import dash_express as dx
import numpy as np
import plotly.express as px

app = dash.Dash(__name__)

# template = dx.templates.FlatDiv()
# template = dx.templates.DccCard(title="Dash Express App", width="500px")
# template = dx.templates.DbcCard(title="Dash Express App", columns=6)
# template = dx.templates.DbcRow(title="Dash Express App")
# template = dx.templates.DbcSidebar(title="Dash Express App")
# template = dx.templates.DdkCard(title="Dash Express App", width=50)
# template = dx.templates.DdkRow(title="Dash Express App")
# template = dx.templates.DdkSidebar(title="Dash Express App")

from ddk_theme import theme
template = dx.templates.DdkSidebar(title="Dash Express App", theme=theme)


@dx.parameterize(
    app,
    inputs=dict(
        figure_title="Initial Title",
        fun=["sin", "cos", "exp"],
        phase=(1, 10),
        amplitude=(1, 10),
    ),
    template=template,
    labels={
        "fun": "Function",
        "figure_title": "Figure Title",
        "phase": "Phase: {}",
        "amplitude": "Amplitude: {}"
    },
    optional=["fun", "phase"],
)
def callback_components(fun, figure_title, phase, amplitude):
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

app.layout = callback_components.layout(app)

if __name__ == "__main__":
    app.run_server(debug=True)
