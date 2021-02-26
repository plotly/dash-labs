import plotly.express as px
import dash_labs as dl
import dash
import pandas as pd

df = px.data.tips()

app = dash.Dash(__name__, plugins=[dl.Plugin()])
tpl = dl.templates.DbcCard(title="Table Component Plugin")

# serverside = False
serverside = True
table_plugin = dl.component_plugins.DataTablePlugin(
    df=df, page_size=10, template=tpl, sort_mode="single", filterable=True,
    serverside=serverside
)

@app.callback(
    args=[
        tpl.dropdown(["Male", "Female"], label="Patron Gender", clearable=True),
        table_plugin.args
    ],
    output=[table_plugin.output, tpl.graph()],
    template=tpl,
)
def callback(gender, table_input):
    if gender:
        filtered_df = df.query(f"sex == {repr(gender)}")
    else:
        filtered_df = df

    dff = table_plugin.get_processed_dataframe(table_input, filtered_df)

    fig = px.scatter(
        dff, x="total_bill", y="tip", color="sex", color_discrete_map={"Male": "green", "Female": "orange"},
    )

    return [table_plugin.build(table_input, dff, preprocessed=True), fig]

app.layout = tpl.layout(app)

if __name__ == "__main__":
    app.run_server(debug=True)
