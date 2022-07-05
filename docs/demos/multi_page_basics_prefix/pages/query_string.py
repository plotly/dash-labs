from dash_labs.plugins import register_page
from dash import dcc, html

register_page(__name__, path="/dashboard")


def layout(velocity=None, **other_unknown_query_strings):
    return html.Div([dcc.Input(id="velocity", value=velocity)])
