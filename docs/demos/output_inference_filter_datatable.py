import dash
import dash_express as dx
import plotly.express as px
tips = px.data.tips()
import dash_html_components as html
import dash_core_components as dcc

app = dash.Dash(__name__, plugins=[dx.Plugin()])

@app.callback(
    inputs=dict(
        tip_range=dx.Input(dcc.RangeSlider(min=0, max=20, value=(5, 10)), label="Tip range"),
        sex=dx.Input(["Male", "Female"], label="Patron Gender"),
    ),
)
def filter_table(tip_range, sex):
    # Let parameterize infer output component
    filtered = tips

    if tip_range is not None:
        filtered = filtered.query(f"tip >= {tip_range[0]} & tip <= {tip_range[1]}")

    if sex is not None:
        filtered = filtered.query(f"sex == '{sex}'")

    return [
        dcc.Markdown("### Filtered tips plot"),
        px.scatter(filtered, x="total_bill", y="tip"),
        html.Hr(),
        dcc.Markdown("### Filtered tips table"),
        filtered,
    ]


app.layout = filter_table.layout(app)

if __name__ == "__main__":
    app.run_server(debug=True)
