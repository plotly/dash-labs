import dash
import dash_labs as dl
import plotly.express as px
import plotly.graph_objects as go
import dash_bootstrap_components as dbc

app = dash.Dash(__name__, plugins=[dl.plugins.FlexibleCallbacks()])

df = px.data.gapminder()
df = df[[c for c in df.columns if not c.startswith("iso_")]]
years = sorted(df.year.drop_duplicates())
continents = list(df.continent.drop_duplicates())

tabs = dict(scatter="Scatter", hist="Histogram", table="Table")

tpl = dl.templates.DbcSidebarTabs(
    app,
    tabs,
    title=f"Dash Labs App",
    theme=dbc.themes.DARKLY,
    figure_template=True,
)

table_plugin = dl.component_plugins.DataTablePlugin(
    df.iloc[:0],
    sort_mode="single",
    role="table",
    page_size=15,
    serverside=True,
    filterable=True,
)

year_label_plugin = dl.component_plugins.DynamicLabelPlugin(
    tpl.slider_input(
        years[0],
        years[-1],
        step=5,
        value=years[-1],
        label="Year: {}",
        tooltip=False,
    )
)


@app.callback(
    args=dict(
        continent=tpl.checklist_input(continents, value=continents, label="Continents"),
        year_args=year_label_plugin.args,
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
        year_label_plugin.output,
        dl.Output(
            dbc.Label(children="Current Tab: ", className="h5"),
            "children",
            role="input",
        ),
    ],
    template=tpl,
)
def callback(year_args, continent, logs, table_inputs, tab):

    # Get year value from plugin
    year = year_label_plugin.get_value(year_args)
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
        year_label_plugin.get_output_values(year_args),
        "Current Tab: " + tabs[tab],
    )


app.layout = dbc.Container(fluid=True, children=tpl.children)

if __name__ == "__main__":
    app.run_server(debug=True)
