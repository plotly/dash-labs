import dash

import dash_express as dx
import plotly.express as px
import dash_html_components as html
import dash_core_components as dcc

from table_plugin import Table

tips = px.data.tips()
app = dash.Dash(__name__, plugins=[dx.Plugin()])

template = dx.templates.DbcSidebar(title="Dash Express App")
# template = dx.templates.DdkSidebar(title="Dash Express App", sidebar_width="400px", show_editor=True)
# template = dx.templates.DccCard(title="Dash Express App")

graph_id = dx.build_id(name="output-graph")
graph = template.Graph(id=graph_id)

num_selected_input_id = dx.build_id(name="output-table")
num_selected_input = template.Input(id=num_selected_input_id)

# Build serverside table parts
table_plugin = Table(tips, serverside=True)

@app.callback(
    inputs=dict(
        max_total_bill=dx.Input(dcc.Slider(min=0, max=50.0, value=0.25), label="Max total bill ($)"),
        tip_range=dx.Input(dcc.RangeSlider(min=0, max=20, value=(5, 10)), label="Tip range ($)"),
        sex=dx.Input(dcc.Dropdown(
            options=[{"value": v, "label": v} for v in ["Male", "Female"]]
        ), label="Patron Gender"),
        table_values=table_plugin.inputs,
        selectedData=dx.Input(graph_id, "selectedData"),
    ),
    template=template,
    output=[
        dx.Output(graph, "figure"),
        table_plugin.output,
        dx.Output(num_selected_input_id, "value")
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

    return [fig, table_plugin.build(table_values, df=filtered), num_selected]


layout = filter_table.layout(app)
layout.children.insert(0, num_selected_input)

app.layout = layout

if __name__ == "__main__":
    app.run_server(debug=True)
