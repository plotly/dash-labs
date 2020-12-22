import dash
import dash_express as dx
import plotly.express as px
import dash_core_components as dcc
tips = px.data.tips()
import dash_html_components as html
from dash_table import DataTable

app = dash.Dash(__name__)
# template = dx.templates.DbcSidebar(title="Dash Express App")
template = dx.templates.DdkSidebar(title="Dash Express App", sidebar_width="400px", show_editor=True)
# template = dx.templates.DccCard(title="Dash Express App")


table_id = dx.build_component_id(kind="datatable", name="output-table")
table = DataTable(
    id=table_id,
    columns=[
        {"name": i, "id": i} for i in sorted(tips.columns)
    ],
    page_size=10,
)


@dx.parameterize(
    app,
    input=dict(
        max_total_bill=(0, 50.0, 0.25),
        tip_range=dcc.RangeSlider(min=0, max=20, value=(5, 10)),
        sex=["Male", "Female"],
    ),
    template=template,
    labels={
        "max_total_bill": "Max total bill ($): {:.2f}",
        "tip_range": lambda v: "Tip range ($): " + (f"{v[0]:.2f} - {v[1]:.2f}" if v else "None"),
        "sex": "Patron Gender",
    },
    optional=["max_total_bill", "max_tip", "sex", "tip_range"],
    output=(table, "data"),
)
def filter_table(max_total_bill, tip_range, sex):
    # Let parameterize infer output component
    filtered = tips

    if max_total_bill is not None:
        filtered = filtered.query(f"total_bill < {max_total_bill}")

    if tip_range is not None:
        filtered = filtered.query(f"tip >= {tip_range[0]} & tip <= {tip_range[1]}")

    if sex is not None:
        filtered = filtered.query(f"sex == '{sex}'")

    return filtered.to_dict('records')


app.layout = filter_table.layout

if __name__ == "__main__":
    app.run_server(debug=True, port=9077)
