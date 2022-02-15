from dash import html, dcc

import dash

dash.register_page(__name__)


import pprint
registry = {a:{c:d for c, d in b.items() if c != 'layout'} for a, b in dash.page_registry.items()}
pprint.pprint(registry, compact=True)


text = dcc.Markdown(
    """
## Welcome to a live demo of the `/pages` multi-page app API.  

For more details, see the [Overview]() and the [Reference]() section.  

[dashlabs_docs]() code


This page is  `demo_home.py` in the `pages/multi_page_demo` folder.  It's registered like this:

```python

import dash

dash.register_page(__name__)

```


Since nothing is specified, everything in `dash.page_registry` is inferred automatically:

- `"module": "pages.multi_page_demo.home"`  The module path where this page's layout is defined. Often `__name__`.  `

- `"path": "/multi-page-demo/home"`   See it in the URL

- `"name": "Demo Home"` The name of the link. If not supplied, will be inferred from module. See it in the sidebar.

- `"order": None` No order was supplied.  The links in the sidebar were created by looping through the `dash.page_registry`.
 This page is the first link because it's sorted alpha-numeric by filename.

- `"title": "Demo Home"` The name of the page `<title>`.  See the title in the browser for this page. 

- `description: ""` The <meta type="description"></meta>. If not supplied, then nothing is supplied.

- `"image": "app.jpeg"` The meta description image used by social media platforms. If not supplied, then it looks for the following images in the `assets/` folder:

   - A page specific image: assets/<title>.<extension> is used
   - A generic app image at assets/app.<extension>
   - A logo at assets/logo.<extension> 

- `layout`: The layout function or component for this page. If not supplied, then looks for layout from within the supplied module.
In this example, the layout is defined in the `demo_home.py` file.

Here's how a link to this page shared on social media looks.  



Next: [meta_tags]() 
 
"""
)

layout = html.Div(text)
