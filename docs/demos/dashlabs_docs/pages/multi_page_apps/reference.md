---
register_page:
    name: "Reference"
    order: 1
    title: "Pages Reference"
    description: "Dash Labs documentation"
---

# Multi-Page Dash App Plugin Reference


## `dash.register_page`


`dash.register_page` Assigns the variables to `dash.page_registry` as an `OrderedDict` 
(ordered by `order`). 

`dash.page_registry` is used by `pages_plugin` to set up the layouts as 
a multi-page Dash app. This includes the URL routing callbacks 
(using `dcc.Location`) and the HTML templates to include title,
meta description, and the meta description image.

`dash.page_registry` can also be used by Dash developers to create the 
page navigation links or by template authors.

```python
def register_page(
    module,
    path=None,
    path_template=None,
    name=None,
    order=None,
    title=None,
    description=None,
    image=None,
    redirect_from=None,
    layout=None,
    **kwargs,
):
```


- `module`:
   The module path where this page's `layout` is defined. Often `__name__`.

- `path`:
   URL Path, e.g. `/` or `/home-page`.
   If not supplied, will be inferred from `module`,
   e.g. `pages.weekly_analytics` to `/weekly-analytics`

- `path_template`:
       Add variables to a URL by marking sections with <variable_name>. The layout function
       then receives the <variable_name> as a keyword argument.
       e.g. path_template= "/asset/<asset_id>"
            then if pathname in browser "/assets/a100" then layout will receive **{"asset_id":"a100"}

- `name`:
   The name of the link.
   If not supplied, will be inferred from `module`,
   e.g. `pages.weekly_analytics` to `Weekly analytics`

- `order`:
   The order of the pages in `page_registry`.
   If not supplied, then the filename is used and the page with path `/` has
   order `0`

- `title`:
   The name of the page `<title>`. That is, what appears in the browser title.
   If not supplied, will use the supplied `name` or will be inferred by module,
   e.g. `pages.weekly_analytics` to `Weekly analytics`

- `description`:
   The `<meta type="description"></meta>`.
   If not supplied, then nothing is supplied.
    
- `image`:
   The meta description image used by social media platforms.
   If not supplied, then it looks for the following images in `assets/`:
    - A page specific image: `assets/<title>.<extension>` is used, e.g. `assets/weekly_analytics.png`
    - A generic app image at `assets/app.<extension>`
    - A logo at `assets/logo.<extension>`
  When inferring the image file, it will look for the following extensions: APNG, AVIF, GIF, JPEG, PGN, SVG, WebP

- `redirect_from`:
   A list of paths that should redirect to this page.
   For example: `redirect_from=['/v2', '/v3']`

- `layout`:
   The layout function or component for this page.
   If not supplied, then looks for `layout` from within the supplied `module`.

- `**kwargs`:
   Arbitrary keyword arguments that can be stored.

-----------------

### Inferred vs supplied properties

`page_registry` stores the original property that was passed in under 
`supplied_<property>` and the inferred property under `<property>`. 
For example, if this was called:
```
register_page(
    'pages.historical_outlook',
    name='Our historical view',
    custom_key='custom value'
)
```
Then this will appear in `page_registry`:
```python
OrderedDict([
    (
        'pages.historical_outlook', 
        dict(
            module='pages.historical_outlook',
            
            supplied_path=None,
            path='/historical-outlook',
            
            supplied_name='Our historical view',
            name='Our historical view',
            
            supplied_title=None,
            title='Our historical view',
            
            supplied_layout=None,
            layout=<function pages.historical_outlook.layout>,
            
            custom_key='custom value'
        )
    ),
])
```


### `@callback` vs `@app.callback`
####`clientside_callback` vs `app.clientside_callback`

With `/pages` it's necessary to use `@callback` instead of `@app.callback` for callbacks located in the `pages/` folder.



In Dash 1.0, `callback` and `clientside_callback` were bound to `app`:
```python
from dash import callback, clientside_callback
@app.callback(...)
def update(..):
    # ...

app.clientside_callback(
    # ...
)

```
This is still supported in 2.0.

In Dash 2.0, `callback` and `clientside_callback` are now also available from the `dash` module and can be defined without `app`:

```python
from dash import callback, clientside_callback

@callback(...)
def update(..):
    # ...

clientside_callback(
    # ...
)
```

Or equivalently:
```python
import dash

@dash.callback(...)
def update(..):
    # ...

dash.clientside_callback(
    # ...
)
```

This is particularly useful in two cases:
1. Organizing your Dash app into multiple files, like when creating [multi-page apps](https://dash.plotly.com/urls). In Dash 1.0, it was easy to run into a circular import error and we recommended creating a new entry point to your app called `index.py` while keeping your `app` inside `app.py`. In 2.0, you no longer need to reorganize your code this way.
2. Packaging components & callbacks for others to use such as All-in-One Components. 

There are three limitations with `dash.callback`:
1. The global level `prevent_initial_callbacks` via `app = dash.Dash(__name__, prevent_initial_callbacks=True)` is not supported. It defaults to `False`. This is still configurable on a per-callback level.
2. `dash.long_callback` is not yet supported.
3. `@dash.callback` will not work if your project has multiple `app` declarations. Some members of the community have used this pattern to create multi-page apps instead of the official [`dcc.Location` multi-page app solution.](https://dash.plotly.com/urls).
The multi-app pattern was never officially documented or supported by our team.  We built and officially support the `dcc.Location` method of multiple pages vs multiple flask instances for a couple of reasons:

    - “Single page app (SPA)” links with dcc.Link: This allows page navigation without reloading the browser page (and therefore reloading and re-evaluating the JS scripts and CSS), making page navigation quite a bit faster
    - Ability to share common components in the “frame” of the page rather than redefining within each page like headers and sidebars
    - Ability to share data like dcc.Store
    - More easily use query parameters in dash callbacks
    - “It’s just Dash” - dcc.Location and dcc.Link provide a multi page app experience using the same simple foundational principles of dash: Rich components tied together with callback functions
Now with `/pages`, we’re adding even more functionality out of the box (see overview page) that you would otherwise need to program from scratch using the flask method.


### Coming Soon to Dash 2.2.0

- `dash.get_relative_path`
- `dash.strip_relative_path`
- `dash.get_asset_url`

This is similar to `dash.callback` where you don't need the `app` object. It makes it possible to use these functions in the `pages` folder of a multi-page app without running into the circular `app` imports issue.
