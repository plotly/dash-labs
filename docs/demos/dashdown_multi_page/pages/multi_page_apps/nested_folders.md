---
dash.register_page(
    __name__,
    name="Nested Folders",
    order=2,
    layout=dashdown(
        "pages/multi_page_apps/nested_folders.md",
        exec_code=False,
        #  code_card_style={"margin": "25px 50px"}
    ),
)

---


# Multi-Page Dash App Plugin Examples

### Example: Nested Folders
This example shows how `dash.register_page` handles
  - Using Nested folders in `pages/` 
  - Storing icons as arbitrary keyword arguments

See the code in `/demos/multi-page-nested-folders`

In larger multi-page apps it's common to organize topics into categories. Each category may have its own folder with multiple 
pages. This plugin automatically searches all subdirectories in `pages/` and includes all the apps.
In our example the `heatmaps.py` is in `pages/` and  `pie-chart.py` is in `pages/chapter/`.
The `dash.page_registry` dictionary will include the subdirectory name(s) in the dict key and the module and path like this:

```python
OrderedDict([
    ('pages.heatmaps', {
        'module': 'pages.heatmap', 
        'path': '/heatmap',
         ...
        }
    ),
    ('pages.chapter.pie-chart', {
        'module': 'pages.chapter.pie-chart', 
        'path': '/chapter/pie-chart',
         ...
        }
    ),
    ...
])

```

In this example app, we will create a sidebar nav for the app pages located in the `chapter/` folder.  We use a `dbc.Offcanvas()` component and open the sidebar nav with a button.

Here is the `app.py`

```python
import dash
from dash import dcc, html, Output, Input, State
import dash_labs as dl
import dash_bootstrap_components as dbc


app = dash.Dash(
    __name__,
    plugins=[dl.plugins.pages],
    external_stylesheets=[dbc.themes.BOOTSTRAP, dbc.icons.FONT_AWESOME],
)


navbar = dbc.NavbarSimple(
    dbc.DropdownMenu(
        [
            dbc.DropdownMenuItem(page["name"], href=page["path"])
            for page in dash.page_registry.values()
            if not page["path"].startswith("/chapter")
        ],
        nav=True,
        label="More Pages",
    ),
    brand="Multi Page App Plugin Demo",
    color="primary",
    dark=True,
    className="mb-2",
)

sidebar_button = dbc.Button(html.I(className="fa fa-bars"), id="sidebar-btn")
sidebar = dbc.Offcanvas(
    dbc.Nav(
        [html.H3("Chapters")]
        + [
            dbc.NavLink(
                [
                    html.I(className=page["icon"]),
                    html.Span(page["name"], className="ms-2"),
                ],
                href=page["path"],
                active="exact",
            )
            for page in dash.page_registry.values()
            if page["path"].startswith("/chapter")
        ],
        vertical=True,
        pills=True,
    ),
    id="offcanvas",
)

app.layout = dbc.Container(
    [
        navbar,
        dbc.Row(
            [
                dbc.Col([sidebar_button], width=1),
                dbc.Col([sidebar, dl.plugins.page_container]),
            ]
        ),
    ],
    fluid=True,
)


@app.callback(
    Output("offcanvas", "is_open"),
    Input("sidebar-btn", "n_clicks"),
    State("offcanvas", "is_open"),
)
def toggle_theme_offcanvas(n1, is_open):
    if n1:
        return not is_open
    return is_open


if __name__ == "__main__":
    app.run_server(debug=True)

```

Recall from the previous chapter that  `dash.register_page` also accepts arbitrary keyword arguments. We use this
feature to store the icon used in the nav for each page. 

Here is how we store the FontAwesome icon for `pages/chapter/pie-chart.py`

```python

dash.register_page(__name__, icon="fas fa-chart-pie")
```

You can see how the icon is included in the sidebar navigation:

![nested_folders](https://user-images.githubusercontent.com/72614349/140660047-d97e80b0-72dd-4fbe-b862-55f5a6431331.gif)
