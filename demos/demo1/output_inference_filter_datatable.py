import dash
import dash_express as dx
import plotly.express as px
tips = px.data.tips()
import dash_html_components as html
import dash_core_components as dcc

app = dash.Dash(__name__)

@dx.parameterize(
    app,
    inputs=dict(
        tip_range=dcc.RangeSlider(min=0, max=20, value=(5, 10)),
        sex=["Male", "Female"],
    ),
    labels={
        "tip_range": "Tip range ($): {} - {}",
        "sex": "Patron Gender",
    },
    optional=["max_total_bill", "max_tip", "sex", "tip_range"]
)
def filter_table(tip_range, sex):
    # Let parameterize infer output component
    filtered = tips

    if tip_range is not None:
        filtered = filtered.query(f"tip >= {tip_range[0]} & tip <= {tip_range[1]}")

    if sex is not None:
        filtered = filtered.query(f"sex == '{sex}'")

    return [
        "### Filtered tips plot",
        px.scatter(filtered, x="total_bill", y="tip"),
        html.Hr(),
        "### Filtered tips table",
        filtered,
    ]


app.layout = filter_table.layout(app)

if __name__ == "__main__":
    app.run_server()
