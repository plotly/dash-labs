import dash
from dash import html


dash.register_page(
    __name__,
    path="/",
    name="Analytic Apps",
    description="Welcome to my app",
    order=0,
    redirect_from=["/old-home-page", "/v2"],
    extra_template_stuff="yup",
)

layout = html.Div("Home Page")
