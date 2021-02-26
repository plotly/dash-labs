import plotly.express as px
import dash_labs as dl
import dash

df = px.data.tips()

app = dash.Dash(__name__, plugins=[dl.Plugin()])

table_plugin = dl.component_plugins.DataTablePlugin(
    df=df, page_size=10, sort_mode="single", filterable=True, serverside=True,
)

table_plugin.install_callback(app)
app.layout = table_plugin.components_div

if __name__ == "__main__":
    app.run_server(debug=True)
