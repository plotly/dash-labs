import dash
from dash_bootstrap_templates import ThemeSwitchAIO
import dash_bootstrap_components as dbc

template_theme1 = "flatly"
template_theme2 = "darkly"
url_theme1 = dbc.themes.FLATLY
url_theme2 = dbc.themes.DARKLY

dash.register_page(__name__)

from dash import Dash, dcc, html, Input, Output, callback
import plotly.express as px

df = px.data.tips()
days = df.day.unique()


def layout():
    return html.Div(
        [
            dcc.Dropdown(
                id="dropdown",
                options=[{"label": x, "value": x} for x in days],
                value=days[0],
                clearable=False,
            ),
            dcc.Graph(id="bar-chart"),
        ],
    )


@callback(
    Output("bar-chart", "figure"),
    Input("dropdown", "value"),
    Input(ThemeSwitchAIO.ids.switch("theme"), "value"),
)
def update_bar_chart(day, toggle):
    template = template_theme1 if toggle else template_theme2
    mask = df["day"] == day
    fig = px.bar(
        df[mask],
        x="sex",
        y="total_bill",
        color="smoker",
        barmode="group",
        template=template,
    )
    return fig
