import dash
import dash_labs as dl
import dash_bootstrap_components as dbc
import dash_html_components as html
import plotly.express as px
import plotly.graph_objects as go

app = dash.Dash(__name__, plugins=[dl.plugins.FlexibleCallbacks()])

# Load and preprocess gapminder dataset
gapminder_df = px.data.gapminder()
years = sorted(gapminder_df.year.drop_duplicates())
continents = list(gapminder_df.continent.drop_duplicates())

# Make template for Gapminder row
gapminder_tpl = dl.templates.DbcRow(app, figure_template=True)


@app.callback(
    args=dict(
        year=gapminder_tpl.slider_input(
            years[0], years[-1], step=5, value=years[-1], label="Year"
        ),
        continent=gapminder_tpl.checklist_input(
            continents, value=continents, label="Continents"
        ),
        logs=gapminder_tpl.checklist_input(
            ["log(x)"],
            value="log(x)",
            label="Axis Scale",
        ),
    ),
    output=gapminder_tpl.graph_output(),
    template=gapminder_tpl,
)
def gapminder_callback(year, continent, logs):
    # Let parameterize infer output component
    year_df = gapminder_df[gapminder_df.year == year]
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


# Load and preprocess tips dataset
tips_df = px.data.tips()

# Make template for tips row
tips_tpl = dl.templates.DbcCard(app, figure_template=True)


@app.callback(
    args=tips_tpl.checklist_input(["No", "Yes"], value=["No", "Yes"], label="Smoker"),
    output=tips_tpl.graph_output(),
    template=tips_tpl,
)
def tips_callback(smoker):
    plot_tips_df = tips_df[tips_df.smoker.isin(smoker)]
    if len(plot_tips_df) == 0:
        return go.Figure()

    return px.histogram(
        plot_tips_df,
        x="total_bill",
        y="tip",
        color="sex",
        marginal="rug",
        hover_data=tips_df.columns,
    )


# Create final tabbed layout
app.layout = dbc.Container(
    fluid=True,
    style={"padding": 20},
    children=[
        html.Div(
            children=[
                html.H2("Data Explorer"),
                html.Hr(),
                dbc.Tabs(
                    [
                        dbc.Tab(
                            dbc.Card(gapminder_tpl.children, body=True),
                            label="Gapminder",
                        ),
                        dbc.Tab(dbc.Card(tips_tpl.children, body=True), label="Tips"),
                    ]
                ),
            ]
        )
    ],
)


if __name__ == "__main__":
    app.run_server(debug=True)
