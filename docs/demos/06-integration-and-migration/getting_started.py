import dash
import dash_labs as dl
import dash_bootstrap_components as dbc
import plotly.express as px

# Make app and template
app = dash.Dash(__name__, plugins=[dl.plugins.FlexibleCallbacks()])
tpl = dl.templates.DbcCard(app, "Gapminder", figure_template=True)

# Load and preprocess dataset
df = px.data.gapminder()
years = sorted(df.year.drop_duplicates())


@app.callback(
    args=tpl.slider_input(years[0], years[-1], step=5, value=years[-1], label="Year"),
    output=tpl.graph_output(),
    template=tpl,
)
def callback(year):
    # Let parameterize infer output component
    year_df = df[df.year == year]
    title = f"Life Expectancy ({year})"
    return (
        px.scatter(
            year_df,
            x="gdpPercap",
            y="lifeExp",
            size="pop",
            color="continent",
            hover_name="country",
            size_max=60,
            title=title,
        )
        .update_layout(margin=dict(l=0, r=0, b=0), height=400)
        .update_traces(marker_opacity=0.8)
    )


app.layout = dbc.Container(fluid=True, children=tpl.children)

if __name__ == "__main__":
    app.run_server(debug=True)
