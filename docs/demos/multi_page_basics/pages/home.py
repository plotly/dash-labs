import dash
from dash import html


dash.register_page(
    __name__,
    name="Analytic Apps",
    description="Welcome to my app",
    redirect_from=["/old-home-page", "/v2"],
    extra_template_stuff="yup",
)

layout = html.Div("Home Page")
