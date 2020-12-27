import dash
import dash_express as dx
import plotly.express as px
from filter_table_plugin import FilterTable

template = dx.templates.DbcCard(title="Scatter Selection")

tips = px.data.tips()
filter_table_plugin = FilterTable(
    tips, px_kwargs=dict(x="total_bill", y="tip"), page_size=12, template=template
)

app = dash.Dash(__name__)

@dx.parameterize(
    app,
    template=template,
    inputs=[filter_table_plugin.inputs],
    output=filter_table_plugin.output,
)
def filter_table(inputs_value):
    print(filter_table_plugin.selection_indices(inputs_value))
    return filter_table_plugin.build(inputs_value)


app.layout = filter_table.layout(app)

if __name__ == "__main__":
    app.run_server(debug=True)
