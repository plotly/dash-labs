import dash
from dash_bootstrap_templates import ThemeSwitchAIO
import dash_bootstrap_components as dbc
template_theme1 = "flatly"
template_theme2 = "darkly"
url_theme1 = dbc.themes.FLATLY
url_theme2 = dbc.themes.DARKLY

dash.register_page(__name__, path="/")

from dash import Dash, dcc, html, Input, Output, callback
import plotly.express as px

df = px.data.medals_wide(indexed=True)

layout = html.Div(
    [
        html.P("Medals included:"),
        dcc.Checklist(
            id="heatmaps-medals",
            options=[{"label": x, "value": x} for x in df.columns],
            value=df.columns.tolist(),
        ),
        dcc.Graph(id="heatmaps-graph"),
    ]
)


@callback(Output("heatmaps-graph", "figure"), Input("heatmaps-medals", "value"),Input(ThemeSwitchAIO.ids.switch("theme"), "value"))
def filter_heatmap(cols, toggle):
    template = template_theme1 if toggle else template_theme2
    fig = px.imshow(df[cols], template=template)
    return fig
