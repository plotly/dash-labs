from dash import html

from dash_labs.plugins import register_page

register_page(__name__, path="/404")


layout = html.H1("Custom 404")
