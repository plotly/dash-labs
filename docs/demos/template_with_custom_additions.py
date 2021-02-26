import dash
import dash_labs as dl
import numpy as np
import dash_core_components as dcc
import plotly.express as px

app = dash.Dash(__name__, plugins=[dl.Plugin()])
tpl = dx.templates.DbcSidebar(title="Dash Labs App")

# import dash_core_components as dcc
@app.callback(
    inputs=dict(
        fun=dx.Input(dcc.Dropdown(
            options=[{"value": v, "label": v} for v in ["sin", "cos", "exp"]],
            value="sin",
        ), label="Function"),
        figure_title=dx.Input(dcc.Input(value="Initial Title"), label="Figure Title"),
        phase=dx.Input(dcc.Slider(min=1, max=10, value=3), label="Phase"),
        amplitude=dx.Input(dcc.Slider(min=1, max=10, value=4), label="Amplitude")
    ),
    template=tpl,
)
def function_browser(fun, figure_title, phase, amplitude):
    xs = np.linspace(-10, 10, 100)
    return dcc.Graph(figure=px.line(
        x=xs, y=getattr(np, fun)(xs + phase) * amplitude
    ).update_layout(title_text=figure_title))


# Add extra component to template
tpl.add_component(
    dcc.Markdown(children="# First Group"), role="input", before="fun"
)

tpl.add_component(dcc.Markdown(children=[
    "# Second Group\n"
    "Specify the Phase and Amplitudue for the chosen function"
]), role="input", before="phase")


tpl.add_component(dcc.Markdown(children=[
    "# H2 Title\n",
    "Here is the *main* plot"
]), role="output", before=0)

tpl.add_component(
    dcc.Link("Made with Dash", href="https://dash.plotly.com/"),
    component_property="children", role="output"
)

app.layout = tpl.layout(app)

if __name__ == "__main__":
    app.run_server(debug=True)
