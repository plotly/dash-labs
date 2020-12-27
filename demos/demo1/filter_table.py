import dash
import dash_express as dx
import plotly.express as px
from dash.dependencies import Input
import dash_core_components as dcc

tips = px.data.tips()

app = dash.Dash(__name__)
graph_id = dx.build_id("graph")
template = dx.templates.DbcCard(title="Scatter Selection")

@dx.parameterize(
    app,
    template=template,
    inputs=dict(
        selectedData=Input(graph_id, "selectedData"),
    ),
    output=[
        (dcc.Graph(id=graph_id), "figure"),
        (template.DataTable(
            columns=[{"name": i, "id": i} for i in tips.columns],
            page_size=10
        ), "data")
    ],
)
def filter_table(selectedData):
    # Let parameterize infer output component
    if selectedData:
        inds = [p["pointIndex"] for p in selectedData["points"]]
        filtered = tips.iloc[inds]
    else:
        filtered = tips
        inds = None

    figure = px.scatter(
        tips, x="total_bill", y="tip"
    ).update_traces(
        type="scatter", selectedpoints=inds
    ).update_layout(dragmode="select")

    return [
        figure,
        filtered.to_dict('records'),
    ]


app.layout = filter_table.layout(app)

if __name__ == "__main__":
    app.run_server(debug=True)
