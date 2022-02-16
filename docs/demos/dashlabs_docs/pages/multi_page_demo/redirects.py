import dash
from dash import html, dcc


dash.register_page(__name__, redirect_from=["/old-home-page", "/v2"])

text = dcc.Markdown(
    """
## Redirects

 A redirect is when a web page is visited at a certain URL, it changes to a different URL. 

Define the redirects with the  `redirect_from` prop:

```python

dash.register_page(
    __name__,
    redirect_from=["/old-home-page", "/v2"]
)

```

Try changing the URL to  /old-home-page  or /v2 and see this page displayed.

Previous [Query Strings](https://dashlabs.pythonanywhere.com/multi-page-demo/query-string)
"""
)

layout = html.Div(
    [
        text,
        html.H1("My New Home Page"),
        html.Br(),
    ]
)
