from dash_labs.plugins import register_page

from dash import dcc, html, Input, Output, callback
import plotly.express as px

register_page(__name__, icon="fas fa-chart-pie")

df = px.data.tips()


layout = html.Div(
    [
        html.P("Names:"),
        dcc.Dropdown(
            id="names",
            value="day",
            options=[
                {"value": x, "label": x} for x in ["smoker", "day", "time", "sex"]
            ],
            clearable=False,
        ),
        html.P("Values:"),
        dcc.Dropdown(
            id="values",
            value="total_bill",
            options=[{"value": x, "label": x} for x in ["total_bill", "tip", "size"]],
            clearable=False,
        ),
        dcc.Graph(id="pie-chart"),
    ]
)


@callback(
    Output("pie-chart", "figure"), [Input("names", "value"), Input("values", "value")]
)
def generate_chart(names, values):
    fig = px.pie(df, values=values, names=names)
    return fig
