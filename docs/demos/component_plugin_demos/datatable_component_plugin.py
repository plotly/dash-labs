import plotly.express as px
import dash_express as dx
import dash

df = px.data.tips()

app = dash.Dash(__name__, plugins=[dx.Plugin()])
tp = dx.templates.DbcCard(title="Clientside Table Component Plugin")

# serverside = False
serverside = True
table_plugin = dx.component_plugins.DataTablePlugin(
    df=df, page_size=10, sort_mode="single", filterable=True,
    serverside=serverside, template=tp
)


@app.callback(
    args=[
        tp.dropdown(["Male", "Female"], label="Patron Gender", clearable=True),
        table_plugin.inputs
    ],
    output=table_plugin.output
)
def callback(gender, plugin_input):
    if gender:
        filtered_df = df.query(f"sex == {repr(gender)}")
    else:
        filtered_df = df
    return table_plugin.build(plugin_input, filtered_df)

app.layout = callback.layout(app)

if __name__ == "__main__":
    app.run_server(debug=True)
