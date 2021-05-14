import plotly.express as px
import dash_labs as dl
import dash_bootstrap_components as dbc
import dash

df = px.data.tips()

app = dash.Dash(__name__, plugins=[dl.plugins.FlexibleCallbacks()])
tpl = dl.templates.DbcCard(app, title="DataTablePlugin")

table_plugin = dl.component_plugins.DataTablePlugin(
    df=df,
    page_size=10,
    sort_mode="single",
    filterable=True,
    serverside=False,
    template=tpl,
)

table_plugin.install_callback(app)
app.layout = dbc.Container(fluid=True, children=tpl.children)

if __name__ == "__main__":
    app.run_server(debug=True)
