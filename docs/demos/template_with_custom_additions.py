import dash
import dash_labs as dl
import numpy as np
import dash_core_components as dcc
import dash_bootstrap_components as dbc
import plotly.express as px

app = dash.Dash(__name__, plugins=[dl.plugins.FlexibleCallbacks()])
tpl = dl.templates.DbcSidebar(app, title="Dash Labs App")

# import dash_core_components as dcc
@app.callback(
    inputs=dict(
        fun=tpl.new_dropdown(["sin", "cos", "exp"], label="Function"),
        figure_title=tpl.new_textbox("Initial Title", label="Figure Title"),
        phase=tpl.new_slider(1, 10, value=3, label="Phase"),
        amplitude=tpl.new_slider(1, 10, value=4, label="Amplitude"),
    ),
    output=tpl.new_graph(),
    template=tpl,
)
def function_browser(fun, figure_title, phase, amplitude):
    xs = np.linspace(-10, 10, 100)
    return px.line(x=xs, y=getattr(np, fun)(xs + phase) * amplitude).update_layout(
        title_text=figure_title
    )


# Add extra component to template
tpl.add_component(
    dcc.Markdown(children="# First Group"), location="sidebar", before="fun"
)

tpl.add_component(
    dcc.Markdown(
        children=[
            "# Second Group\n"
            "Specify the Phase and Amplitudue for the chosen function"
        ]
    ),
    location="sidebar",
    before="phase",
)


tpl.add_component(
    dcc.Markdown(children=["# H2 Title\n", "Here is the *main* plot"]),
    location="main",
    before=0,
)

tpl.add_component(
    dcc.Link("Made with Dash", href="https://dash.plotly.com/"),
    component_property="children",
    location="main",
)

app.layout = dbc.Container(fluid=True, children=tpl.children)

if __name__ == "__main__":
    app.run_server(debug=True)
