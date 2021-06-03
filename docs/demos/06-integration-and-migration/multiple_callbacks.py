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


@app.callback(
    args=tpl.new_slider(
        years[0],
        years[-1],
        step=5,
        value=years[-1],
        label="Year",
        id="slider",
    ),
    output=tpl.new_graph(id="gap-minder-graph"),
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
            custom_data=["country"],
        )
        .update_layout(margin=dict(l=0, r=0, b=0), height=400)
        .update_traces(marker_opacity=0.8)
    )


@app.callback(
    args=[dl.Input("gap-minder-graph", "clickData"), dl.Input("slider", "value")],
    output=tpl.new_graph(),
    template=tpl,
)
def callback(click_data, year):
    if click_data:
        country = click_data["points"][0]["customdata"][0]
        country_df = df[df["country"] == country]
        return (
            px.line(country_df, x="year", y="lifeExp", title=country)
            .add_vline(year, line_color="lightgray")
            .update_layout(height=300)
            .update_yaxes(range=[30, 100])
        )
    else:
        return go.Figure(layout_height=300).update_yaxes(range=[30, 100])


app.layout = dbc.Container(fluid=True, children=tpl.children)


if __name__ == "__main__":
    app.run_server(debug=True)
