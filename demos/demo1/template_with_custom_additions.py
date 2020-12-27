import dash
import dash_express as dx
import numpy as np
import dash_core_components as dcc
import plotly.express as px
from ddk_theme import theme
import dash_html_components as html

app = dash.Dash(__name__)
# template = dx.templates.DdkSidebar(title="Dash Express App", theme=theme, sidebar_width="450px", show_editor=True)
template = dx.templates.DbcSidebar(title="Dash Express App")
# template = dx.templates.DccCard(title="Dash Express App")

# import dash_core_components as dcc
@dx.parameterize(
    app,
    inputs=dict(
        fun=["sin", "cos", "exp"],
        figure_title="Initial Title",
        phase=(1, 10),
        amplitude=(1, 10)
    ),
    template=template,
    labels={
        "fun": "Function",
        "figure_title": "Figure Title",
        "phase": "Phase: {}",
        "amplitude": "Amplitude: {}"
    },
)
def function_browser(fun, figure_title, phase, amplitude):
    xs = np.linspace(-10, 10, 100)
    return template.Graph(figure=px.line(
        x=xs, y=getattr(np, fun)(xs + phase) * amplitude
    ).update_layout(title_text=figure_title))


# Add extra component to template
template.add_markdown("# First Group", role="input", before="fun")
template.add_markdown([
    "# Second Group\n"
    "Specify the Phase and Amplitudue for the chosen function"
],
    role="input", before="phase")

template.add_markdown([
    "# H2 Title\n",
    "Here is the *main* plot"
], role="output", before=0)

template.add_component(
    dcc.Link("Made with Dash", href="https://dash.plotly.com/"),
    role="output", value_property="children"
)

app.layout = function_browser.layout(app)

if __name__ == "__main__":
    app.run_server(debug=True, port=9034)
