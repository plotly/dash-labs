# Based on https://dash-bootstrap-components.opensource.faculty.ai/examples/iris/

import dash_express as dx
import plotly.express as px
import dash_core_components as dcc
import dash_bootstrap_components as dbc
from dash.dependencies import Input, Output
import dash


# Load data
df = px.data.iris()
feature_cols = [col for col in df.columns if "species" not in col]
feature_labels = [col.replace("_", " ").title() + " (cm)" for col in feature_cols]
feature_options = [
    {"label": label, "value": col} for col, label in zip(feature_cols, feature_labels)
]

# Build app and template
app = dash.Dash(__name__)
# template = dx.templates.DbcSidebar(title="Iris Features")
template = dx.templates.DdkSidebar(title="Iris Features")


# Use interact to create components
def iris(x, y):
    return template.build_graph(
        figure=px.scatter(df, x=x, y=y, color="species"),
    )


layout = dx.parameterize(
    app,
    iris,
    params=dict(
        x=dbc.Select(options=feature_options, value="sepal_length"),
        y=dbc.Select(options=feature_options, value="sepal_width")
    ),
    template=template,
)


app.layout = layout


# make sure that x and y values can't be the same variable
def filter_options(v):
    """Disable option ability to plot x vs x"""
    return [
        {"label": label, "value": col, "disabled": col == v}
        for col, label in zip(feature_cols, feature_labels)
    ]

# TODO: dx.select to get sliders
# # functionality is the same for both dropdowns, so we reuse filter_options
# app.callback(Output("x-variable", "options"), [Input("y-variable", "value")])(
#     filter_options
# )
#
# app.callback(Output("y-variable", "options"), [Input("x-variable", "value")])(
#     filter_options
# )


if __name__ == "__main__":
    app.run_server(debug=True, port=9007)
