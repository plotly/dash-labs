import dash
import dash_labs as dl
import numpy as np
import dash_bootstrap_components as dbc
import plotly.express as px
import plotly.graph_objects as go

app = dash.Dash(__name__, plugins=[dl.plugins.FlexibleCallbacks()])

df = px.data.gapminder()
df = df[[c for c in df.columns if not c.startswith("iso_")]]
years = sorted(df.year.drop_duplicates())
continents = list(df.continent.drop_duplicates())

# theme_name = "cerulean"
# theme_name = "cosmo"
# theme_name = "cyborg"
# theme_name = "darkly"
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

# css_url = f"https://bootswatch.com/4/{theme_name}/bootstrap.css"
# Or, use local file path to assets folder
# css_url = "assets/custom_bootstrap.css"

# tabs = ["scatter", "hist", "table"]
tabs = dict(scatter="Scatter", hist="Histogram", table="Table")

tpl = dl.templates.DbcSidebarTabs(
    app,
    tabs,
    # title=f"Dash Labs - {theme_name.title()} Theme",
    title=f"Dash Labs - Default Theme",
    figure_template=True,
)


table_plugin = dl.component_plugins.DataTablePlugin(
    df.iloc[:0],
    sort_mode="single",
    role="table",
    page_size=15,
    serverside=False,
    filterable=True,
)


@app.callback(
    args=dict(
        continent=tpl.checklist_input(continents, value=continents, label="Continents"),
        year=tpl.slider_input(
            years[0], years[-1], step=5, value=years[-1], label="Year"
        ),
        logs=tpl.checklist_input(
            ["log(x)"], value="log(x)", label="Axis Scale", role="scatter"
        ),
        table_inputs=table_plugin.args,
        tab=tpl.tab_input(),
    ),
    output=[
        tpl.graph_output(role="scatter"),
        tpl.graph_output(role="hist"),
        table_plugin.output,
    ],
    template=tpl,
)
def callback(year, continent, logs, table_inputs, tab):
    print(f"tab_id: {tab}")
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

    return (
        scatter_fig,
        hist_fig,
        table_plugin.get_output_values(table_inputs, df=year_df),
    )


app.layout = dbc.Container(fluid=True, children=tpl.children)

if __name__ == "__main__":
    app.run_server(debug=True)
