import dash_express as dx

import dash
from templates.base import BaseTemplate
from dash.dependencies import Input, Output, ALL
import dash_html_components as html
import plotly.express as px


plot_encodings = dict(
    scatter=["x", "y", "color", "symbol", "size"],
    scatter_3d=["x", "y", "z", "color", "symbol", "size"],
    line=["x", "y", "line_group", "color", "line_dash"],
    area=["x", "y", "line_group", "color"],
    bar=["x", "y", "color", "facet_row"],
    histogram=["x", "y", "color"],
    violin=["x", "y", "color"],
)


def px_builder(app, df, template: BaseTemplate):
    # Let template class configure app

    # Configure app
    template.configure_app(app)

    # Build template instance
    template_instance = template.instance()

    columns = df.columns.tolist()
    output = html.Div(id="output-div")

    @app.callback(
        Output("output-div", "children"),
        [template.all_component_ids()])
    def callback(_):
        # Get inputs list and build map from component names to prior values
        inputs_list = dash.callback_context.inputs_list
        prior_values = {e["id"]["name"]: e["value"] for e in inputs_list[0] if "value" in e}

        # Handle wrapping output Div in app wrapper
        template_instance = template.instance(full=False)

        # Plot type
        plot_type = prior_values.get("plot_type", "scatter")
        template_instance.add_dropdown(
            options=list(plot_encodings), value=plot_type,
            label="Plot Type: {value}", role="input", name="plot_type"
        )

        # Build encoding dropdowns
        plot_kwargs = dict()
        for key in plot_encodings[plot_type]:
            if key in ["x", "y", "z"]:
                default = columns[0]
                clearable = False
            else:
                default = None
                clearable = True

            val = prior_values.get(key, default) or None
            plot_kwargs[key] = val
            template_instance.add_dropdown(
                options=columns, value=val, label=key, name=key, role="input", clearable=clearable,
            )

        # Build output graph
        fig = getattr(px, plot_type)(df, **plot_kwargs)
        template_instance.add_graph(fig, name="output_graph")

        return template_instance.layout

    return template_instance.maybe_wrap_layout(output)
