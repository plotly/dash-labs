import dash
import dash_express as dx
import plotly.express as px
tips = px.data.tips()
import dash_html_components as html
from dash.dependencies import Input
import dash_core_components as dcc


app = dash.Dash(__name__)

graph_id = dx.build_id("graph")

@dx.parameterize(
    app,
    template=dx.templates.DbcCard(title="Scatter Selection"),
    inputs=dict(
        selectedData=Input(graph_id, "selectedData"),
    ),
    output=[
        (dcc.Graph(id=graph_id), "figure"),
        (html.Div(), "children")
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
        [filtered],
    ]


app.layout = filter_table.layout(app)

if __name__ == "__main__":
    app.run_server(debug=True)
