import plotly.express as px
import dash_labs as dl
import dash

df = px.data.tips()

app = dash.Dash(__name__, plugins=[dl.Plugin()])
tpl = dl.templates.DbcCard(title="Table Component Plugin")

# serverside = False
serverside = True
table_plugin = dl.component_plugins.DataTablePlugin(
    df=df,
    page_size=10,
    sort_mode="single",
    filterable=True,
    serverside=serverside,
    template=tpl,
)


@app.callback(
    args=[
        tpl.dropdown_input(["Male", "Female"], label="Patron Gender", clearable=True),
        table_plugin.args,
    ],
    output=table_plugin.output,
    template=tpl,
)
def callback(gender, plugin_input):
    if gender:
        filtered_df = df.query(f"sex == {repr(gender)}")
    else:
        filtered_df = df
    return table_plugin.get_output_values(plugin_input, filtered_df)


app.layout = tpl.layout(app)

if __name__ == "__main__":
    app.run_server(debug=True)
