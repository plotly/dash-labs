import dash
import dash_express as dx
import numpy as np
import dash_core_components as dcc
import plotly.express as px
from ddk_theme import theme
import dash_html_components as html

app = dash.Dash(__name__, plugins=[dx.Plugin()])
# template = dx.templates.DdkSidebar(title="Dash Express App", theme=theme, sidebar_width="450px", show_editor=True)
template = dx.templates.DbcSidebar(title="Dash Express App")
# template = dx.templates.DccCard(title="Dash Express App")

# import dash_core_components as dcc
@app.callback(
    inputs=dict(
        fun=dx.arg(["sin", "cos", "exp"], label="Function"),
        figure_title=dx.arg("Initial Title", label="Figure Title"),
        phase=dx.arg((1, 10), label="Phase"),
        amplitude=dx.arg((1, 10), label="Amplitude")
    ),
    template=template,
)
def function_browser(fun, figure_title, phase, amplitude):
    xs = np.linspace(-10, 10, 100)
    return template.Graph(figure=px.line(
        x=xs, y=getattr(np, fun)(xs + phase) * amplitude
    ).update_layout(title_text=figure_title))


# Add extra component to template
template.add_component(
    template.Markdown("# First Group"),
    role="input", before="fun"
)

template.add_component(
    template.Markdown([
        "# Second Group\n"
        "Specify the Phase and Amplitudue for the chosen function"
    ]),
    role="input", before="phase")

template.add_component(
    template.Markdown([
        "# H2 Title\n",
        "Here is the *main* plot"
    ]),
    role="output", before=0)

template.add_component(
    dcc.Link("Made with Dash", href="https://dash.plotly.com/"),
    role="output", value_property="children"
)

app.layout = function_browser.layout(app)

if __name__ == "__main__":
    app.run_server(debug=True)
