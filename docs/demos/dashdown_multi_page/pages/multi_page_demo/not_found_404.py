from dash import html, dcc
import dash

dash.register_page(__name__)


text = dcc.Markdown(
    """
## Custom 404 page

This page is  `not_found_404.py` in the `pages/` folder.  It's registered like this:

```python

import dash

dash.register_page(__name__)

```

If you have `not_found_404.py` in the root of the `pages` folder, then that page will be displayed instead of
 just "404" when a page cannot be found. Try entering some random path in the URL. You will see this page displayed.

"""
)

layout = html.Div(text)
