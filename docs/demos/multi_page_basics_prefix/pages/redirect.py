from dash_labs.plugins import register_page
from dash import html
from dash import get_asset_url


register_page(
    __name__,
    description="Welcome to my app",
    redirect_from=["/old-home-page", "/v2"],
    extra_template_stuff="yup",
)

layout = html.Div(
    ["Home Page", html.Img(src=get_asset_url("birds.jpeg"), height="50px")]
)
