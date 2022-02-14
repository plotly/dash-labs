from dash import html, dcc

import dash

dash.register_page(__name__)

text = dcc.Markdown(
    """
## Welcome to the multi page app demo.

This is a minimal example of the features available for multi-page apps.  See the [code]()

This page is  `demo_home.py` in the `pages/multi_page_demo` folder.  It's registered like this:

```python

import dash

dash.register_page(__name__)

```

Since nothing is specified, everything is inferred automatically:

- `module`: The module path where this page's layout is defined. Often `__name__`.  In this case, `__name__` is  `pages.multi_page_demo.home`

- `path`: Look at the URL and you will see it's:   /multi-page-demo/home

- `name`: The name of the link. If not supplied, will be inferred from module.  As you can see in the sidebar, the link name is `Demo Home`

- `order`: No order was specified, so if you create the links by looping through the `dash.page_registry` this page will show 
first because it's sorted in alpha-numeric order by filename.

- `title`: The name of the page `<title>`.  Note that the title in the browser is `Demo Home`

- `description`: The <meta type="description"></meta>. If not supplied, then nothing is supplied.

- `image`: The meta description image used by social media platforms. If not supplied, then it looks for the following images in assets/:

   - A page specific image: assets/<title>.<extension> is used, e.g. assets/weekly_analytics.png
   - A generic app image at assets/app.<extension>
   - A logo at assets/logo.<extension> When inferring the image file, it will look for the following extensions: APNG, AVIF, GIF, JPEG, PGN, SVG, WebP
In this case, since no image is supplied, the closest match is the `app.jpeg` file in the assets folder.  


- `layout`: The layout function or component for this page. If not supplied, then looks for layout from within the supplied module.
In this case, the layout defined here in the `demo_home.py` file.
 
"""
)

layout = html.Div(text)
