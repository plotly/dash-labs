from dash import html
from dash_labs.plugins import register_page

register_page(__name__, path="/", top_nav=True)


layout = html.Div("Home page content")
