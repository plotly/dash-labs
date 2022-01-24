---

dash.register_page(
    __name__,
    name="Sub Menus",
    order=4,
    layout=dashdown(
        "pages/multi_page_apps/sub_menus.md",
        exec_code=False,
        #   code_card_style={"margin": "25px 50px"}
    ),
)
---

# Multi-Page Dash App Examples

### Example: Create navigation options by page

In all the examples so far, the navigation has been the same for all pages of the app. In this example we will show how to
have different navigation options based on which page is displayed.

See how the sidebar is displayed only when the "Topics" link is selected:

![layout_functions](https://user-images.githubusercontent.com/72614349/147510416-3529dabd-6cf4-4e4f-b7a6-027267778b88.gif)



Here is the multi-page structure
```
- app.py
- pages  
  |-- about.py  
  |-- home.py
  |-- side_bar.py  
  |-- topic_1.py  
  |-- topic_2.py  
  |-- topic_3.py  
```


Below is the code for the main `app.py`.  The top `navbar`, which is the same for all pages is defined here.  We
create the nav links by looping through `dash.page_registry` and selecting the apps with the prop `top_nav`. See
how this prop is added to `dash.page_registry` below.  

```python
import dash
import dash_labs as dl
import dash_bootstrap_components as dbc


app = dash.Dash(
    __name__,
    plugins=[dl.plugins.pages],
    external_stylesheets=[dbc.themes.BOOTSTRAP],
)

navbar = dbc.NavbarSimple(
    dbc.Nav(
        [
            dbc.NavLink(page["name"], href=page["path"])
            for page in dash.page_registry.values()
            if page.get("top_nav")
        ],
    ),
    brand="Multi Page App Demo",
    color="primary",
    dark=True,
    className="mb-2",
)

app.layout = dbc.Container(
    [navbar, dl.plugins.page_container],
    fluid=True,
)

if __name__ == "__main__":
    app.run_server(debug=True)

```

This is the `home.py` file. (The `about.py` and `topic_1.py` files are similar).  Since we can add arbitrary props to
 `dash.page_registry`, we add `top_nav=True` here just to make it easy to select which pages to include in the top navbar.


```python
from dash import html
import dash

dash.register_page(__name__, top_nav=True)


layout = html.Div("About page content")

```


We define the sidebar in `side_bar.py` which is in the `pages` folder.  We create the sidebar links by looping
through `dash.page_registry` and selecting the apps with pathnames that starts with `"/topic"`. This sidebar is imported in `topic_1.py, topic_2.py` and `topic_3.py` and
is included in the layout.  Note that `topic_1.py` is both in the top navbar and the sidenav.  It acts as a
landing page for the "topics" section.

Note that `sidebar` is a function.  This is important -- more on this later. 

```python
import dash
from dash import html
import dash_bootstrap_components as dbc


def sidebar():
    return html.Div(
        dbc.Nav(
            [
                dbc.NavLink(
                    [
                        html.Div(page["name"], className="ms-2"),
                    ],
                    href=page["path"],
                    active="exact",
                )
                for page in dash.page_registry.values()
                if page["path"].startswith("/topic")
            ],
            vertical=True,
            pills=True,
            className="bg-light",
        )
    )

```

Here is `topic_2.py`  (`topic_1.py` and `topic_3.py` are similar).  Note that the layout is also a function. 
 
As you see below, `topic_2.py` and `topic_3.py` will NOT have `top_nav=True` included in `dash.register_page`,
but `topic_1.py` will include `top_nav=True` because we want that page in the navbar.

```python
from dash import html

import dash
import dash_bootstrap_components as dbc

from .side_bar import sidebar

dash.register_page(__name__)


def layout():
    return dbc.Row(
        [dbc.Col(sidebar(), width=2), dbc.Col(html.Div("Topic 2 content"), width=10)]
    )

```

The main purpose of this example is to show how to use `dash.page_registry` from within the `pages` folder.  
The reason `sidebar` and the layouts for the three topic pages need to be functions is that pages are added to
`dash.register_page`as each module is imported from the `pages` folder and `dash.register_page` is called.
If you don't use a function then all the pages may not yet be in `dash.page_registry` when it's used to create thing 
like the sidebar. When you use a function, it will create the layout when it's used rather than when it's imported.

