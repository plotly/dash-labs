import dash_express as dx
import plotly.express as px
import dash_core_components as dcc
import dash_bootstrap_components as dbc
from dash.dependencies import Input, Output
import dash

df = px.data.iris()
feature_cols = [col for col in df.columns if "species" not in col]
feature_labels = [col.replace("_", " ").title() + " (cm)" for col in feature_cols]
feature_options = [
    {"label": label, "value": col} for col, label in zip(feature_cols, feature_labels)
]

app = dash.Dash(__name__)


x_dropdown = dbc.Select(id="x-variable", options=feature_options, value="sepal_length")
y_dropdown = dbc.Select(id="y-variable", options=feature_options, value="sepal_width")

@dx.interact(
    dx.layouts.dbc.DbcSidebarLayout(app, title="Iris"),
    labels={"x": "X variable", "y": "Y variable"}
)
def iris(
        x=x_dropdown,
        y=y_dropdown
):
    return dcc.Graph(
        figure=px.scatter(df, x=x, y=y, color="species")
    )


# make sure that x and y values can't be the same variable
def filter_options(v):
    """Disable option v"""
    return [
        {"label": label, "value": col, "disabled": col==v}
        for col, label in zip(feature_cols, feature_labels)
    ]

# functionality is the same for both dropdowns, so we reuse filter_options
app.callback(Output("x-variable", "options"), [Input("y-variable", "value")])(
    filter_options
)

app.callback(Output("y-variable", "options"), [Input("x-variable", "value")])(
    filter_options
)


if __name__ == "__main__":
    iris.run_server(debug=True)
