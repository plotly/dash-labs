from dash import html

from dash_labs.plugins import register_page

register_page(__name__, top_nav=True)


layout = html.Div("About page content")
