---
register_page:
    name: "Overview"
    path: "/"
    order: 0
    title: "Pages Overview"
    description: "Dash Labs documentation"

---
# Multi-Page Dash App Plugin

### Background

> **[See the community announcement for details and discussion](https://community.plotly.com/t/introducing-dash-pages-dash-2-1-feature-preview/57775)**


The goal of this plugin is to remove as much boilerplate as possible when creating multi-page Dash apps.

This plugin allows users to simply place their layouts in `pages/` and call `dash.register_page` with the desired URL path of that page.

This plugin will automatically:
- Create the URL routing callback
- Add page information to `dash.page_registry` that can be used when creating navigation bars
- Set `validate_layout` accordingly so that you don't need to `suppress_callback_exceptions` for simple multi-page layouts
- Set the order of `dash.page_registry` based off `order`  and the filename
- Set `<title>` and `<meta description>` and their social media equivalents accordingly in the `index_string` of the HTML that is served on page-load
- Set the social media meta image accordingly based off of images available in assets
- Set a clientside callback to update the `<title>` as you navigate pages with `dcc.Link`

- Make it possible to specify a list of URLs that will be redirected to the page.
- Make it possible to add arbitrary page information to `dash.page_registry`

### Usage

**Quick start examples**

In the folder /demos/multi_page_basics you will find three quick start apps:
- [demos/multi_page_basics/app.py](demos/multi_page_basics/app.py) is a minimal quick start example.
- [demos/multi_page_basics/app_dbc.py](demos/multi_page_basics/app.py) uses a navbar from `dash-bootstrap-components` library to create a navigation header.
- [demos/multi_page_basics/app_ddk.py](demos/multi_page_basics/app.py)  for Dash Enterprise customers using the Design Kit.

These apps serve as an entry point to run the multi-page app and provides some minimal examples of the basic and advanced
features available in the API.

**Creating a simple Multi-Page App**

Now we will step through creating a simple multi-page app.  You will find this example [demos/multi-page-example1/app.py](demos/multi_page_example1/app.py)

1. In `app.py`, pass the plugin into `Dash`.  Note: In the future, this will be part of `dash` and you won't need to do this step.
2. In this example, we create a navigation header using the `NavbarSimple` component from the `dash-bootstrap-components` library and populate
the page names and nav links by looping through the `dash.page_registry` dictionary. (More on page_registry in step 4)
3. Include `dl.plugins.page_container` in the `app.layout`  This is where the page content is rendered.

```python
import dash
import dash_labs as dl
import dash_bootstrap_components as dbc


app = dash.Dash(
    __name__, plugins=[dl.plugins.pages], external_stylesheets=[dbc.themes.BOOTSTRAP]
)

navbar = dbc.NavbarSimple(
    dbc.DropdownMenu(
        [
            dbc.DropdownMenuItem(page["name"], href=page["path"])
            for page in dash.page_registry.values()
            if page["module"] != "pages.not_found_404"
        ],
        nav=True,
        label="More Pages",
    ),
    brand="Multi Page App Plugin Demo",
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

4. Create a folder called `pages/` and place your app layouts in files within that folder. Each file needs to:
- Define `layout`. This can be a variable or function that returns a component
- Call `dash.register_page(__name__)` to tell `dl.plugins.pages` that this page should be part of the multi-page framework

For example, here is the first page of our app:

[`demos/multi-page-example1/pages/heatmaps.py`](docs/demos/multi-page-example1/pages/heatmaps.py)

```python
import dash
dash.register_page(__name__, path="/")
from dash import Dash, dcc, html, Input, Output, callback
import plotly.express as px

df = px.data.medals_wide(indexed=True)

layout = html.Div(
    [
        html.P("Medals included:"),
        dcc.Checklist(
            id="heatmaps-medals",
            options=[{"label": x, "value": x} for x in df.columns],
            value=df.columns.tolist(),
        ),
        dcc.Graph(id="heatmaps-graph"),
    ]
)


@callback(Output("heatmaps-graph", "figure"), Input("heatmaps-medals", "value"))
def filter_heatmap(cols):
    fig = px.imshow(df[cols])
    return fig

```

The `dash.page_registry` is an `OrderedDict` with keys being the page's module name (e.g. `pages.bar-charts`) and values being a dictionary containing keys `path`, `name`, `order`, `title`, `description`, `image`, and `layout`. 
As you saw in the above example, This `page_registry` is populated from calling `dash.register_page` within `pages/`.
`dash.register_page` will accept various arguments to customize aspects about the page.  See the Advanced Features section below.
   

```python dangerously_use_exec=True
html.Img(src="https://user-images.githubusercontent.com/72614349/140232399-efe7020d-480a-40af-a0b0-40e66dcd9d56.gif", className="img-fluid")

```

***

# Advanced Features

These features are all optional. If you don't supply values here, the framework will take a best guess and supply them for you.

**Custom Meta Tags & Titles**

The page's title defines what you see in your browser tab and what would appear as the website's title in search results. By default, it is derived from the filename but it can also be set with `title=`
```python dangerously_use_exec=False
dash.register_page(__name__, title='Custom page title')
```

Similarly, the meta description can be set with `description=` and the meta image can be set with `image=`. Both of these tags are used as the preview when sharing a URL in a social media platforms. They're also used in search engine results.

By default, Dash will look through your `assets/` folder for an image that matches the page's filename or else an image called `app.<image_extension>` (e.g. `app.png` or `app.jpeg`) or `logo.<image_extension>` (all image extensions are supported).

This image URL can also be set directly with `app.register_page(image=...)` e.g. 
```python
app.register_page(__name__, image='/assets/page-preview.png')
```

**`dash.page_registry`**

`dash.page_registry` is an [`OrderedDict`](https://docs.python.org/3/library/collections.html#collections.OrderedDict). The keys are the module as set by `__name__`, e.g. `pages.historical_analysis`. The value is a dict with the parameters passed into `register_page`: `path` `name`, `title`, `description`, `image`, `order`, and `layout`. If these parameters aren't supplied, then they are derived from the filename.

For example:
`pages/historical_analysis.py`
```
dash.register_page(__name__)

print(dash.page_registry)
```
would print:
```
OrderedDict([
    ('pages.historical_analysis', {
        'module': 'pages.historical_analysis', 
        'name': 'Historical analysis', 
        'title': 'Historical analysis',       
        'order': None,
    }
])
```

Whereas:
`pages/outlook.py`
```
dash.register_page(__name__, path='/future', name='Future outlook', order=4)

print(dash.page_registry)
```
would print:
```
OrderedDict([
    ('pages.outlook', {
        'module': 'pages.outlook', 
        'path': '/future',
        'name': 'Future outlook', 
        'title': 'Future outlook',       
        'order': 4,
    }
])
```

OrderedDict values can be accessed just like regular dictionaries:
```
>>> print(dash.page_registry['pages.historical_analysis']['name'])
'Historical analysis'
```

The order of the items in `page_registry` is based off of the optional `order=` parameter: 
```python
dash.register_page(__name__, order=10)
```

If it's not supplied, then the order is alphanumeric based off of the filename. This order is important when rendering the page menu's dynamically in a loop. The page with the path `/` has `order=0` by default.


**Redirects**

Redirects can be set with the `redirect_from=[...]` parameter in `register_page`:

`pages/historical_analysis.py`
```
dash.register_page(
    __name__,
    path='/historical',
    redirect_from=['/historical-analysis', '/historical-outlook']
)
```

**Custom 404 Pages**

404 pages can display content when the URL isn't found. By default, a simple content is displayed:
```
html.Div([
    html.H2('404 - Page not found'),
    html.Div(html.A('Return home', href='/')
])
```

However, this can be customized by creating a file called `not_found_404.py`


**Defining Multiple Pages within a Single File**

You can also pass `layout=` directly into `register_page`. Here's a quick multi-page app written in a single file:
```
app.register_page('historical_analysis', path='/historical-analysis', layout=html.Div(['Historical Analysis Page'])
app.register_page('forecast', path='/forecast', layout=html.Div(['Forecast Page'])

app.layout = dbc.Container([
    dbc.NavbarSimple([
        dbc.NavItem(dbc.NavLink(page['name'], href=page['path'])),
        for page in dash.page_registry
    ]),
    
    dash.page_container
])
```
However, we recommend splitting out the page layouts into their own files in `pages/` to keep things more organized and to keep your files from becoming too long!

**Query Strings**

It's possible to pass query strings from the url to a layout function.
For example:
```python
import dash

dash.register_page(__name__, path='/dashboard')

def layout(velocity=0, **other_unknown_query_strings):
    return dash.html.Div([
        dash.dcc.Input(id='velocity', value=velocity)
    ])

```

```python  dangerously_use_exec=True
html.Img(src="https://user-images.githubusercontent.com/72614349/146809878-3592c173-9764-4653-89aa-21094288ca0a.png", className="img-fluid")

```
**Path Variable**

Another way to pass variables to the layout is to use the `path_template` parameter in  `dash.register_page`.  You can
define which segments of the path are variables by marking them like this: `<variable_name>`. The layout function then receives the `<variable_name>` as a keyword argument.


For example, if `path_template= "/asset/<asset_id>"`, and the url is `"/assets/a100"`, then the layout
will receive `**{"asset_id":"a100"}`.  Here is an example with two variables in the path:


```python
import dash

dash.register_page(
    __name__,
    path_template="/asset/<asset_id>/department/<dept_id>",
)


def layout(asset_id=None, dept_id=None, **other_unknown_query_strings):
    return dash.html.Div(f"variables from pathname:  asset_id: {asset_id} dept_id: {dept_id}")

```

```python dangerously_use_exec=True
html.Img(src="https://user-images.githubusercontent.com/72614349/146810311-73ab7f24-bb6d-4f4e-b3c5-257917d0180d.png", className="img-fluid")

```
***

**Long Callbacks**

Currently `long_callback` requires the `app` object.  To use long callbacks with `pages/` it's necessary to 
include the `@app.long_callback` in the same file where the `app` is instantiated.   You can find an example
in `/demos/multi_page_long_callback`.
