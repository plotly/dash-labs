import dash
from dash.dependencies import Input, Output

import dash_express as dx
import plotly.express as px
import dash_html_components as html
import dash_core_components as dcc

from table_builder import build_table

tips = px.data.tips()
app = dash.Dash(__name__)
template = dx.templates.DbcSidebar(title="Dash Express App")
# template = dx.templates.DdkSidebar(title="Dash Express App", sidebar_width="400px", show_editor=True)
# template = dx.templates.DccCard(title="Dash Express App")

graph_id = dx.build_component_id(kind="graph", name="output-graph")
graph = template.Graph(id=graph_id)

num_selected_input_id = dx.build_component_id(kind="input", name="output-table")
num_selected_input = template.Input(id=num_selected_input_id)

# Build serverside table parts
table_component, update_table, table_inputs = build_table(tips, serverside=True)


@dx.parameterize(
    app,
    inputs=dict(
        max_total_bill=(0, 50.0, 0.25),
        tip_range=dcc.RangeSlider(min=0, max=20, value=(5, 10)),
        sex=["Male", "Female"],
        table_values=table_inputs,
        selectedData=Input(graph_id, "selectedData"),
    ),
    template=template,
    labels={
        "max_total_bill": "Max total bill ($): {:.2f}",
        "tip_range": lambda v: "Tip range ($): " + (f"{v[0]:.2f} - {v[1]:.2f}" if v else "None"),
        "sex": "Patron Gender",
    },
    optional=["max_total_bill", "max_tip", "sex", "tip_range"],
    output=[
        (graph, "figure"),
        table_component,
        Output(num_selected_input_id, "value")
    ]
)
def filter_table(max_total_bill, tip_range, sex, table_values, selectedData):
    print("table_values", table_values)

    if selectedData:
        num_selected = len(selectedData["points"])
    else:
        num_selected = 0

    # Let parameterize infer output component
    filtered = tips

    if max_total_bill is not None:
        filtered = filtered.query(f"total_bill < {max_total_bill}")

    if tip_range is not None:
        filtered = filtered.query(f"tip >= {tip_range[0]} & tip <= {tip_range[1]}")

    if sex is not None:
        filtered = filtered.query(f"sex == '{sex}'")

    fig = px.scatter(
        filtered, x="total_bill", y="tip"
    ).update_layout(uirevision=True)

    return [fig, update_table(filtered, table_values), num_selected]


layout = filter_table.layout
layout.children.insert(0, num_selected_input)

app.layout = layout

if __name__ == "__main__":
    app.run_server(debug=True, port=9043)
