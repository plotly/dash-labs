---
dash.register_page(
    __name__,
    name="Reference",
    order=1,
    layout=dashdown(
        "pages/multi_page_apps/reference.md",
        exec_code=False,
    ),
)
---

# Multi-Page Dash App Plugin Reference


### `dash.register_page`


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
            if pathname = "/assets/a100" then layout will receive {"asset_id":"a100"}

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
   If not supplied, then the default will be the same as the title.
    
- `image`:
   The meta description image used by social media platforms.
   If not supplied, then it looks for the following images in `assets/`:
    - A page specific image: `assets/<title>.<extension>` is used, e.g. `assets/weekly_analytics.png`
    - A generic app image at `assets/app.<extension>`
    - A logo at `assets/logo.<extension>`

- `redirect_from`:
   A list of paths that should redirect to this page.
   For example: `redirect_from=['/v2', '/v3']`

- `layout`:
   The layout function or component for this page.
   If not supplied, then looks for `layout` from within the supplied `module`.

- `**kwargs`:
   Arbitrary keyword arguments that can be stored.

-----------------


`page_registry` stores the original property that was passed in under 
`supplied_<property>` and the coerced property under `<property>`. 
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
            
            supplied_description=None,
            description='Our historical view',
            
            supplied_order=None,
            order=1,
            
            supplied_layout=None,
            layout=<function pages.historical_outlook.layout>,
            
            custom_key='custom value'
        )
    ),
])
```