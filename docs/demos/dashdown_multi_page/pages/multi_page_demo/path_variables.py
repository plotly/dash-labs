import dash
from dash import html, dcc


def title(asset_id=None, dept_id=None):
    return f"Asset analysis for {asset_id} in {dept_id}"


def description(asset_id=None, dept_id=None):
    return f"This is the Acme Company Asset analysis for {asset_id} in {dept_id}"


dash.register_page(
    __name__,
    path_template="/asset/<asset_id>/department/<dept_id>",
    title=title,
    description=description,
    path="/asset/inventory/department/branch-1001",
)

text = dcc.Markdown(
    """

Give it a try!  Change the branch number or inventory in the path in the browser.


Use the  `path_template` parameter in  `dash.register_page` to define which segments of the path are variables by marking them like this: `<variable_name>`. 
  The layout function then receives the `<variable_name>` as a keyword argument.


This page is  `path_variables.py` in the `pages/multi_page_demo` folder.  It's registered like this:

```python


def title(asset_id=None, dept_id=None):
    return f"Asset analysis for {asset_id} in {dept_id}"


def description(asset_id=None, dept_id=None):
    return f"This is the Acme Company Asset analysis for {asset_id} in {dept_id}"


dash.register_page(
    __name__,
    path_template="/asset/<asset_id>/department/<dept_id>",
    title=title,
    description=description,
    path="/asset/inventory/department/branch-1001",
)

```

In the previous examples, the title and the description were strings.  Here they are functions.  This allows you to customize
the title and description based on the path. 

Note that in this example the path is /assets/inventory/department/branch-1001 and the title is "Asset analysis for inventory in branch-001.

Now change inventory to something else, and change the branch  number.  See how the title is updated.  If you share a link to this
page it will have a customized title and description for this page.

To pass the variables to the layout, make the layout a function:

```

def layout(asset_id=None, dept_id=None, **other_unknown_query_strings):
    return html.Div(        
             f"These variables are passed to the layout from the pathname:  `asset_id: {asset_id} dept_id: {dept_id}`"
           )
    
```


"""
)


def layout(asset_id=None, dept_id=None, **other_unknown_query_strings):
    return html.Div(
        [
            html.H2("Path Variables"),
            html.Br(),
            html.H4("These variables are passed to the layout from pathname:"),
            html.H4(f" asset_id:   {asset_id}"),
            html.H4(f" dept_id:  {dept_id}"),
            text,
        ]
    )
