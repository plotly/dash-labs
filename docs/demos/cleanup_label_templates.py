import dash
import dash_express as dx
import numpy as np
import plotly.express as px
import dash_core_components as dcc

app = dash.Dash(__name__, plugins=[dx.Plugin()])

# template = dx.templates.FlatDiv()
# template = dx.templates.DccCard(title="Dash Express App", width="500px")
# template = dx.templates.DbcCard(title="Dash Express App", columns=6)
# template = dx.templates.DbcRow(title="Dash Express App")
# template = dx.templates.DbcSidebar(title="Dash Express App")
# template = dx.templates.DdkCard(title="Dash Express App", width=50)
# template = dx.templates.DdkRow(title="Dash Express App")
# template = dx.templates.DdkSidebar(title="Dash Express App")

template = dx.templates.DbcSidebar(
    title="Dash Express App",
    theme="https://stackpath.bootstrapcdn.com/bootswatch/4.5.2/cyborg/bootstrap.min.css"
)

# from ddk_theme import theme
# template = dx.templates.DdkSidebar(title="Dash Express App", theme=theme)


@app.callback(
    args=dict(
        fun=dx.Input(dcc.Dropdown(
            options=[{"value": v, "label": v} for v in ["sin", "cos", "exp"]],
            value="sin"
        ), label="Function"),
        figure_title=dx.Input(dcc.Input(value="Initial Title"), label="Figure Title"),
        phase=dx.Input(dcc.Slider(min=1, max=10, value=4), label="Phase"),
        amplitude=dx.Input(dcc.Slider(min=1, max=10, value=3), label="Amplitude"),
    ),
    template=template,
)
def callback_components(fun, figure_title, phase, amplitude):
    xs = np.linspace(-10, 10, 100)
    np_fn = getattr(np, fun)

    # Let parameterize infer output component
    x = xs
    y = np_fn(xs + phase) * amplitude
    return template.Graph(
        figure=px.line(x=x, y=y).update_layout(title_text=figure_title)
    )

app.layout = callback_components.layout(app)

if __name__ == "__main__":
    app.run_server(debug=True)
