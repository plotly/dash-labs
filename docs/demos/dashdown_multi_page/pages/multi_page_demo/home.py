from dash import html, dcc

import dash

dash.register_page(__name__)

text = dcc.Markdown(
    """
## Welcome to the multi page app demo.

This is a minimal example of the features available for multi-page apps.  See the [code]()

This page is  `home.py` in the `pages/multi_page_demo` folder.  It's registered like this:

```python

import dash

dash.register_page(__name__)

```

Since nothing is specified, everything is inferred:

- module: The module path where this page's layout is defined. Often `__name__`.  In this case, it's `pages.multi_page_demo.home`

- path: Look at the path in the browser and you will see it's:   /multi-page-demo/home

- name: The name of the link. If not supplied, will be inferred from module.  As you can see in the sidebar, the link name is `Home`

- order: No order was specified, so if you create the links by looping through the `dash.page_registry` this page will show in
 alpha-numeric order by filename.

- title: The name of the page `<title>`.  Note that the title in the browser is `Home`

- description: The <meta type="description"></meta>. If not supplied, then nothing is supplied.

- image: The meta description image used by social media platforms. If not supplied, then it looks for the following images in assets/:

   - A page specific image: assets/<title>.<extension> is used, e.g. assets/weekly_analytics.png
   - A generic app image at assets/app.<extension>
    - A logo at assets/logo.<extension> When inferring the image file, it will look for the following extensions: APNG, AVIF, GIF, JPEG, PGN, SVG, WebP

- layout: The layout function or component for this page. If not supplied, then looks for layout from within the supplied module.
 
"""
)

layout = html.Div(text)
