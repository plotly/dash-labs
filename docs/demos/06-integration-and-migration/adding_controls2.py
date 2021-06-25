import dash
import dash_labs as dl
import dash_bootstrap_components as dbc
import plotly.express as px
import plotly.graph_objects as go

# Make app and template
app = dash.Dash(__name__, plugins=[dl.plugins.FlexibleCallbacks()])
tpl = dl.templates.DbcCard(app, "Gapminder", figure_template=True)

# Load and preprocess dataset
df = px.data.gapminder()
years = sorted(df.year.drop_duplicates())
continents = list(df.continent.drop_duplicates())


@app.callback(
    args=dict(
        year_range=tpl.new_range_slider(
            min=years[0], max=years[-1], step=5, label="Year"
        ),
        continent=tpl.new_checklist(continents, value=continents, label="Continents"),
        logs=tpl.new_checklist(
            ["log(x)"],
            value="log(x)",
            label="Axis Scale",
        ),
    ),
    output=tpl.new_graph(),
    template=tpl,
)
def callback(year_range, continent, logs):
    # Let parameterize infer output component
    # filter years and calculate mean
    year_df = df[(df.year >= year_range[0]) & (df.year <= year_range[-1])]
    year_df = year_df.groupby(["country", "continent"]).mean().reset_index()
    if continent:
        year_df = year_df[year_df.continent.isin(continent)]

    if not len(year_df):
        return go.Figure()

    title = f"Mean Life Expectancy ({year_range[0]}-{year_range[-1]})"
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


app.layout = dbc.Container(fluid=True, children=tpl.children)

if __name__ == "__main__":
    app.run_server(debug=True)
