import dash
from dash import html, dcc

dash.register_page(
    __name__,
    title="Forward Outlook",
    description="This is the forward outlook for the BirdBrands Company",
    path="/forward-outlook",
    image="birds.jpeg",
)


text = dcc.Markdown(
    """
## Customizing the meta tags

This page is  `meta_tags.py` in the `pages/multi_page_demo` folder.  It's registered like this:

```python

dash.register_page(
    __name__,
    path="/forward-outlook",
    title="Forward Outlook",
    description="This is the forward outlook for the BirdBrands Company",    
    image="birds.jpeg",
)
```
Note that the title in the browser is now "Forward Outlook", and the path is /forward-outlook rather than just 
being derrived from the filename `meta_tags.py.

If you share a link to this page on social media, slack, or on the dash forum, then you will have a preview of the
page with an image, title and description.

Give it a try!

"""
)

layout = html.Div(text)
