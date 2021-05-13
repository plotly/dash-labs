import plotly.express as px
import dash_labs as dl
import dash
import dash_html_components as html
import dash_core_components as dcc


df = px.data.tips()
app = dash.Dash(__name__, plugins=[dl.plugins.FlexibleCallbacks()])


table_plugin = dl.component_plugins.DataTablePlugin(
    df=df,
    page_size=10,
    sort_mode="single",
    filterable=True,
    serverside=True,
)

dropdown = dcc.Dropdown(options=[{"label": v, "value": v} for v in ["Male", "Female"]])


@app.callback(
    args=[dl.Input(dropdown, "value"), table_plugin.args],
    output=table_plugin.output,
)
def callback(gender, plugin_input):
    if gender:
        filtered_df = df.query(f"sex == {repr(gender)}")
    else:
        filtered_df = df
    return table_plugin.get_output_values(plugin_input, filtered_df)


app.layout = html.Div([dropdown, table_plugin.container])

if __name__ == "__main__":
    app.run_server(debug=True)
