from dash import html
from dash_labs.plugins import register_page

import dash_bootstrap_components as dbc

from .side_bar import sidebar

register_page(__name__)


def layout():
    return dbc.Row(
        [dbc.Col(sidebar(), width=2), dbc.Col(html.Div("Topic 3 content"), width=10)]
    )
