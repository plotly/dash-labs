import dash
import dash_labs as dl
import dash_bootstrap_components as dbc
import plotly.express as px
import plotly.graph_objects as go

app = dash.Dash(__name__, plugins=[dl.plugins.FlexibleCallbacks()])

# Load gapminder dataset
df = px.data.gapminder()
years = sorted(df.year.drop_duplicates())
continents = list(df.continent.drop_duplicates())

# # Build Themed Template
# theme_name = "cerulean"
# theme_name = "cosmo"
# theme_name = "cyborg"
theme_name = "darkly"
# theme_name = "flatly"
# theme_name = "journal"
# theme_name = "litera"
# theme_name = "lumen"
# theme_name = "lux"
# theme_name = "materia"
# theme_name = "minty"
# theme_name = "pulse"
# theme_name = "sandstone"
# theme_name = "simplex"
# theme_name = "sketchy"
# theme_name = "slate"
# theme_name = "solar"
# theme_name = "spacelab"
# theme_name = "superhero"
# theme_name = "united"
# theme_name = "yeti"

css_url = f"https://bootswatch.com/4/{theme_name}/bootstrap.css"

tpl = dl.templates.DbcSidebarTabs(
    app,
    ["Scatter", "Histogram"],
    title=f"Dash Labs - {theme_name.title()} Theme",
    theme=css_url,
    figure_template=True,
)


@app.callback(
    args=dict(
        continent=tpl.checklist_input(continents, value=continents, label="Continents"),
        year=tpl.slider_input(
            years[0], years[-1], step=5, value=years[-1], label="Year"
        ),
        logs=tpl.checklist_input(
            ["log(x)"], value="log(x)", label="Axis Scale", role="Scatter"
        ),
        tab=tpl.tab_input(),
    ),
    output=[
        tpl.graph_output(role="Scatter"),
        tpl.graph_output(role="Histogram"),
    ],
    template=tpl,
)
def callback(year, continent, logs, tab):
    print(f"Active Tab: {tab}")
    logs = logs or []

    # Let parameterize infer output component
    year_df = df[df.year == year]
    if continent:
        year_df = year_df[year_df.continent.isin(continent)]

    if not len(year_df):
        return [go.Figure(), go.Figure()]

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
        )
        .update_layout(title_text=title, margin=dict(l=0, r=0, b=0))
        .update_traces(marker_opacity=0.8)
    )

    hist_fig = px.histogram(
        year_df, x="lifeExp", color="continent", barnorm=""
    ).update_layout(
        title_text=title,
    )

    return scatter_fig, hist_fig


app.layout = dbc.Container(fluid=True, children=tpl.children)

if __name__ == "__main__":
    app.run_server(debug=True)
