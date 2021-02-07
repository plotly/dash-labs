import dash
import dash_express as dx
import numpy as np
import plotly.express as px

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
    inputs=dict(
        figure_title=dx.arg("Initial Title", label="Function"),
        fun=dx.arg(["sin", "cos", "exp"], label="Figure Title"),
        phase=dx.arg((1, 10), label="Phase"),
        amplitude=dx.arg((1, 10), label="Amplitude"),
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
