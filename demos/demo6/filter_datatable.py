import dash
import dash_express as dx
import numpy as np
import plotly.express as px
tips = px.data.tips()
import dash_html_components as html

app = dash.Dash(__name__)
template = dx.templates.DbcSidebar(title="Dash Express App")
# template = dx.templates.DdkSidebar(title="Dash Express App")
# template = dx.templates.DccCard(title="Dash Express App")


def filter(max_total_bill, max_tip, sex):
    # Let parameterize infer output component
    return [
        "## Filtered Table",
        html.Hr(),
        tips.query(f"total_bill < {max_total_bill} & tip < {max_tip} & sex == '{sex}'")
    ]


layout = dx.parameterize(
    app,
    filter,
    params=dict(
        max_total_bill=(0, 20.0, 0.25),
        max_tip=(0, 10.0, 0.25),
        sex=["Male", "Female"]
    ),
    template=template,
    labels={
        "max_total_bill": "Max total bill: ${value:.2f}",
        "max_tip": "Max tip: ${value:.2f}",
        "sex": "Patron Gender",
    }
)

app.layout = layout

if __name__ == "__main__":
    app.run_server(debug=True, port=9037)
