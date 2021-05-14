import dash
import dash_labs as dl
import dash_bootstrap_components as dbc
import dash_core_components as dcc
import dash_html_components as html
import plotly.express as px
import plotly.graph_objects as go

# Make app and template
app = dash.Dash(
    __name__,
    plugins=[dl.plugins.FlexibleCallbacks()],
    external_stylesheets=[dbc.themes.FLATLY],
)

# Load and preprocess dataset
df = px.data.gapminder()
years = sorted(df.year.drop_duplicates())
continents = list(df.continent.drop_duplicates())

# Make components
year_slider = dcc.Slider(
    min=years[0],
    max=years[-1],
    step=5,
    value=years[-1],
    tooltip={"placement": "bottom", "always_visible": True},
)

continent_checklist = dbc.Checklist(
    options=[{"value": opt, "label": opt} for opt in continents], value=continents
)

logs_checklist = dbc.Checklist(
    options=[{"value": "log(x)", "label": "log(x)"}], value="log(x)"
)

graph = dcc.Graph()


@app.callback(
    args=dict(
        year=dl.Input(year_slider, "value"),
        continent=dl.Input(continent_checklist, "value"),
        logs=dl.Input(logs_checklist, "value"),
    ),
    output=dl.Output(graph, "figure"),
)
def callback(year, continent, logs):
    # Let parameterize infer output component
    year_df = df[df.year == year]
    if continent:
        year_df = year_df[year_df.continent.isin(continent)]

    if not len(year_df):
        return go.Figure()

    title = f"Life Expectancy ({year})"
    return (
        px.scatter(
            year_df,
            x="gdpPercap",
            y="lifeExp",
            size="pop",
            color="continent",
            hover_name="country",
            log_x="log(x)" in logs,
            size_max=60,
            title=title,
        )
        .update_layout(margin=dict(l=0, r=0, b=0))
        .update_traces(marker_opacity=0.8)
    )


app.layout = dbc.Container(
    fluid=True,
    children=[
        html.H2("Gapminder"),
        html.Hr(),
        dbc.Row(
            [
                dbc.Col(
                    md=4,
                    children=dbc.Card(
                        body=True,
                        children=[
                            dbc.FormGroup(
                                [
                                    dbc.Label("Year", className="h5"),
                                    year_slider,
                                ]
                            ),
                            dbc.FormGroup(
                                [
                                    dbc.Label("Continent", className="h5"),
                                    continent_checklist,
                                ]
                            ),
                            dbc.FormGroup(
                                [
                                    dbc.Label("Axis Scale", className="h5"),
                                    logs_checklist,
                                ]
                            ),
                        ],
                    ),
                ),
                dbc.Col(md=8, children=dbc.Card(body=True, children=graph)),
            ]
        ),
    ],
)

if __name__ == "__main__":
    app.run_server(debug=True)
