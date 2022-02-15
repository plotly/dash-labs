from dash import html, dcc
import dash

dash.register_page(__name__)


text = dcc.Markdown(
    """
## Custom 404 page

This page is  `not_found_404.py` in the `pages/multi_page_demo` folder.  It's registered like this:

```python

import dash

dash.register_page(__name__)

```

If you have a `not_found_404.py` file, then this page will be displayed instead of just "404" when a page cannot be found.
Give it a try!  Enter some random path in the browser.



"""
)

layout = html.Div(text)
