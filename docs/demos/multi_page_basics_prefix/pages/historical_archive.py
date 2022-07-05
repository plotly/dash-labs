from dash import html

from dash_labs.plugins import register_page

register_page(__name__)


def layout():
    return html.H1("Historical Archive")
