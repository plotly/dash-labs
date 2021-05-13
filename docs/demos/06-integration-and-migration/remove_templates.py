import dash
import dash_labs as dl
import dash_bootstrap_components as dbc
import dash_html_components as html
import plotly.express as px
import plotly.graph_objects as go

# Make app and template
app = dash.Dash(__name__, plugins=[dl.plugins.FlexibleCallbacks()], external_stylesheets=[dbc.themes.FLATLY])


# Import general DBC template class to use for component constructors
from dash_labs.templates.dbc import DbcTemplate as tpl

# Load and preprocess dataset
gapminder_df = px.data.gapminder()
years = sorted(gapminder_df.year.drop_duplicates())
continents = list(gapminder_df.continent.drop_duplicates())

# Build iris
year_input = tpl.slider_input(
    years[0], years[-1], step=5, value=years[-1], label="Year"
)
year_slider = year_input.component_id

continent_input = tpl.checklist_input(continents, value=continents, label="Continents")
continent_checklist = continent_input.component_id

logs_input = tpl.checklist_input(
    ["log(x)"], value="log(x)", label="Axis Scale",
)
logs_checklist = logs_input.component_id

graph_output = tpl.graph_output()
graph = graph_output.component_id

@app.callback(
    args=dict(
        year=year_input,
        continent=continent_input,
        logs=logs_input,
    ),
    output=graph_output,
)
def gapminder_callback(year, continent, logs):
    # Let parameterize infer output component
    year_df = gapminder_df[gapminder_df.year == year]
    if continent:
        year_df = year_df[year_df.continent.isin(continent)]

    if not len(year_df):
        return go.Figure()

    title = f"Life Expectancy ({year})"
    scatter_fig = (
        px.scatter(
            year_df,
            x="gdpPercap",
            y="lifeExp",
            size="pop",
            color="continent",
            hover_name="country",
            log_x="log(x)" in logs,
            size_max=60,
            title=title
        )
        .update_layout(margin=dict(l=0, r=0, b=0))
        .update_traces(marker_opacity=0.8)
    )
    return scatter_fig


app.layout = dbc.Container(fluid=True, children=[
    html.Div(children=[
        html.H2("Dash Labs, no template"),
        html.Hr(),
        dbc.FormGroup(children=[
            dbc.Label(children="Graph"),
            graph,
        ]),
        dbc.FormGroup(children=[
            dbc.Label(children="Year"),
            year_slider,
        ]),
        dbc.FormGroup(children=[
            dbc.Label(children="Continent"),
            continent_checklist,
        ]),
        dbc.FormGroup(children=[
            dbc.Label(children="Axis Scale"),
            logs_checklist,
        ]),
    ])
])


if __name__ == "__main__":
    app.run_server(debug=True)
