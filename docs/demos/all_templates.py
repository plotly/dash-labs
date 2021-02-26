import dash
import dash_express as dx
import numpy as np
import dash_core_components as dcc
import plotly.express as px

app = dash.Dash(__name__, plugins=[dx.Plugin()])

tpl = dx.templates.FlatDiv()
# tpl = dx.templates.DccCard(title="Dash Express App", width="500px")
# tpl = dx.templates.DbcCard(title="Dash Express App", columns=6)
# tpl = dx.templates.DbcRow(title="Dash Express App")
# tpl = dx.templates.DbcSidebar(title="Dash Express App")
# tpl = dx.templates.DdkCard(title="Dash Express App", width=50)
# tpl = dx.templates.DdkRow(title="Dash Express App")
# tpl = dx.templates.DdkSidebar(title="Dash Express App")

# tpl = dx.templates.DbcSidebar(
#     title="Dash Express App",
#     theme="https://stackpath.bootstrapcdn.com/bootswatch/4.5.2/cyborg/bootstrap.min.css"
# )

# from my_theme import theme
# tpl = dx.templates.DdkSidebar(title="Dash Express App", theme=theme)


@app.callback(
    args=dict(
        fun=tpl.dropdown(["sin", "cos", "exp"], label="Function"),
        figure_title=tpl.input("Initial Title", label="Figure Title"),
        phase=tpl.slider(1, 10, label="Phase"),
        amplitude=tpl.slider(1, 10, value=3, label="Amplitude"),
    ),
    output=tpl.graph(),
    template=tpl
)
def callback(fun, figure_title, phase, amplitude):
    xs = np.linspace(-10, 10, 100)
    np_fn = getattr(np, fun)

    # Let parameterize infer output component
    x = xs
    y = np_fn(xs + phase) * amplitude
    return px.line(x=x, y=y).update_layout(title_text=figure_title)


app.layout = tpl.layout(app)

if __name__ == "__main__":
    app.run_server(debug=True)
