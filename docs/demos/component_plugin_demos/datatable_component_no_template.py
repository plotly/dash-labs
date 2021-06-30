import plotly.express as px
import dash_labs as dl
import dash_html_components as html
import dash

df = px.data.tips()

app = dash.Dash(__name__, plugins=[dl.plugins.FlexibleCallbacks()])

table_plugin = dl.component_plugins.DataTablePlugin(
    df=df,
    page_size=10,
    sort_mode="single",
    filterable=True,
    serverside=False,
)

table_plugin.install_callback(app)

app.layout = html.Div(
    children=table_plugin.args_components + table_plugin.output_components
)

if __name__ == "__main__":
    app.run_server(debug=True)
