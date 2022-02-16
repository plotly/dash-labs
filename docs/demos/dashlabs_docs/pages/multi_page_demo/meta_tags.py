import dash
from dash import html, dcc

dash.register_page(
    __name__,
    title="Forward Outlook",
    description="This is the forward outlook for ANV Industries",
    path="/forward-outlook",
    image="birds.png",
)


text = dcc.Markdown(
    """
## Meta Tags

For more background information on meta-tags, see the [Customizing Meta Tags]() section.

This page is  `meta_tags.py` in the `pages/multi_page_demo` folder.  It's registered like this:

```python

dash.register_page(
    __name__,
    path="/forward-outlook",
    title="Forward Outlook",
    description="This is the forward outlook for AVN Industries",    
    image="birds.png",
)
```
Note that the title in the browser is now "Forward Outlook", and the URL  is /forward-outlook rather than just 
being derived from the filename `meta_tags.py`.

If you share a link to this page on social media, slack, or on the dash forum, then you will have a preview of the
page with an image, title and description.

Give it a try!  


Next: [Not Found 404](https://dashlabs.pythonanywhere.com/multi-page-demo/not-found-404)  Previous [Demo Home](https://dashlabs.pythonanywhere.com/multi-page-demo/demo-home)
"""
)

layout = html.Div(text)
