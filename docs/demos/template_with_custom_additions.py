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
        fun=tpl.dropdown_input(["sin", "cos", "exp"], label="Function"),
        figure_title=tpl.textbox_input("Initial Title", label="Figure Title"),
        phase=tpl.slider_input(1, 10, value=3, label="Phase"),
        amplitude=tpl.slider_input(1, 10, value=4, label="Amplitude"),
    ),
    output=tpl.graph_output(),
    template=tpl,
)
def function_browser(fun, figure_title, phase, amplitude):
    xs = np.linspace(-10, 10, 100)
    return px.line(x=xs, y=getattr(np, fun)(xs + phase) * amplitude).update_layout(
        title_text=figure_title
    )


# Add extra component to template
tpl.add_component(dcc.Markdown(children="# First Group"), role="input", before="fun")

tpl.add_component(
    dcc.Markdown(
        children=[
            "# Second Group\n"
            "Specify the Phase and Amplitudue for the chosen function"
        ]
    ),
    role="input",
    before="phase",
)


tpl.add_component(
    dcc.Markdown(children=["# H2 Title\n", "Here is the *main* plot"]),
    role="output",
    before=0,
)

tpl.add_component(
    dcc.Link("Made with Dash", href="https://dash.plotly.com/"),
    component_property="children",
    role="output",
)

app.layout = dbc.Container(fluid=True, children=tpl.children)

if __name__ == "__main__":
    app.run_server(debug=True)
