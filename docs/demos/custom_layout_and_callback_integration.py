# Based on https://dash-bootstrap-components.opensource.faculty.ai/examples/iris/

import dash_express as dx
import plotly.express as px
import dash_core_components as dcc
import dash_html_components as html
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


# Use parameterize to create components
@dx.callback(
    app,
    inputs=dict(
        x=dcc.Dropdown(options=feature_options, value="sepal_length"),
        y=dcc.Dropdown(options=feature_options, value="sepal_width"),
    ),
)
def iris(x, y):
    return dcc.Graph(
        figure=px.scatter(df, x=x, y=y, color="species"),
    )

# Get references to the dropdowns and register a custom callback to prevent the user
# from setting x and y to the same variable

# Get the dropdown components that were created by parameterize
x_component = iris.roles["input"]["x"].value
y_component = iris.roles["input"]["y"].value


# Define standalon function that computes what values to enable, reuse for both
# dropdowns with app.callback
def filter_options(v):
    """Disable option ability to plot x vs x"""
    return [
        {"label": label, "value": col, "disabled": col == v}
        for col, label in zip(feature_cols, feature_labels)
    ]

app.callback(Output(x_component.id, "options"), [Input(y_component.id, "value")])(
    filter_options
)

app.callback(Output(y_component.id, "options"), [Input(x_component.id, "value")])(
    filter_options
)

# Build a custom layout, using the parameter *containers* (not values as above)
x_container = iris.roles["input"]["x"].container.component
y_container = iris.roles["input"]["y"].container.component
output_container = iris.roles["output"][0].container.component

app.layout = html.Div([
    html.H1("Iris Feature Explorer"),
    html.H2("Select Features"),
    x_container,
    y_container,
    html.Hr(),
    html.H2("Feature Scatter Plot"),
    output_container
])

if __name__ == "__main__":
    app.run_server(debug=True)
