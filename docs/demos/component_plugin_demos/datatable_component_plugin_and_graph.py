import plotly.express as px
import dash_labs as dl
import dash_bootstrap_components as dbc
import dash
import plotly.io as pio


df = px.data.tips()

app = dash.Dash(__name__, plugins=[dl.plugins.FlexibleCallbacks()])
tpl = dl.templates.DbcSidebar(
    app, title="Table Component Plugin", sidebar_columns=6, figure_template=True
)

serverside = True
table_plugin = dl.component_plugins.DataTablePlugin(
    df=df,
    page_size=10,
    template=tpl,
    sort_mode="single",
    filterable=True,
    serverside=serverside,
    role="input",
)


@app.callback(
    args=[
        tpl.dropdown_input(["Male", "Female"], label="Patron Gender", clearable=True),
        table_plugin.args,
    ],
    output=[table_plugin.output, tpl.graph_output()],
    template=tpl,
)
def callback(gender, table_input):
    if gender:
        filtered_df = df.query(f"sex == {repr(gender)}")
    else:
        filtered_df = df

    dff = table_plugin.get_processed_dataframe(table_input, filtered_df)

    colorway = pio.templates[pio.templates.default].layout.colorway
    fig = px.scatter(
        dff,
        x="total_bill",
        y="tip",
        color="sex",
        color_discrete_map={"Male": colorway[0], "Female": colorway[1]},
    )

    return [table_plugin.get_output_values(table_input, dff, preprocessed=True), fig]


app.layout = dbc.Container(fluid=True, children=tpl.children)

if __name__ == "__main__":
    app.run_server(debug=True)
