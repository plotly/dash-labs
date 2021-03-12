import dash
import dash_labs as dl
import numpy as np
import plotly.express as px

app = dash.Dash(__name__, plugins=[dl.Plugin()])

# tpl = dl.templates.FlatDiv()
tpl = dl.templates.HtmlCard(title="Dash Labs App", width="500px")
# tpl = dl.templates.DbcCard(title="Dash Labs App", columns=6)
# tpl = dl.templates.DbcRow(title="Dash Labs App")
# tpl = dl.templates.DbcSidebar(title="Dash Labs App")
# tpl = dl.templates.DdkCard(title="Dash Labs App", width=50)
# tpl = dl.templates.DdkRow(title="Dash Labs App")
# tpl = dl.templates.DdkSidebar(title="Dash Labs App")

# tpl = dl.templates.DbcSidebar(
#     title="Dash Labs App",
#     theme="https://stackpath.bootstrapcdn.com/bootswatch/4.5.2/cyborg/bootstrap.min.css",
#     figure_template=True,
# )

import dash_bootstrap_components as dbc
tpl = dl.templates.DbcSidebar(
    title="Dash Labs App",
    theme=dbc.themes.CYBORG,
)

# from my_theme import theme
# tpl = dx.templates.DdkSidebar(title="Dash Labs App", theme=theme)


@app.callback(
    args=dict(
        fun=tpl.dropdown_input(["sin", "cos", "exp"], label="Function"),
        figure_title=tpl.textbox_input("Initial Title", label="Figure Title"),
        phase=tpl.slider_input(1, 10, label="Phase"),
        amplitude=tpl.slider_input(1, 10, value=3, label="Amplitude"),
    ),
    output=tpl.graph_output(),
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
