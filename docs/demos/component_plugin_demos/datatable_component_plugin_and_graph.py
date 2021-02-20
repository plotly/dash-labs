import plotly.express as px
import dash_express as dx
import dash
import pandas as pd

df = px.data.tips()

app = dash.Dash(__name__, plugins=[dx.Plugin()])
tp = dx.templates.DbcCard(title="Clientside Table Component Plugin")

# serverside = False
serverside = True
table_plugin = dx.component_plugins.DataTablePlugin(
    df=df, page_size=10, template=tp, sort_mode="single", filterable=True,
    serverside=serverside
)


@app.callback(
    args=[
        tp.dropdown(["Male", "Female"], label="Patron Gender", clearable=True),
        table_plugin.inputs
    ],
    output=[table_plugin.output, tp.graph()]
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

app.layout = callback.layout(app)

if __name__ == "__main__":
    app.run_server(debug=True)
