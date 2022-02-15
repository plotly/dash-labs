import dash
from dash import html, dcc
from textwrap import dedent


def title(asset_id=None, dept_id=None):
    return f"Asset Analysis: {asset_id} {dept_id}"


def description(asset_id=None, dept_id=None):
    return f"This is the AVN Industries Asset Analysis: {asset_id} in {dept_id}"


dash.register_page(
    __name__,
    path_template="/asset/<asset_id>/department/<dept_id>",
    title=title,
    description=description,
    path="/asset/inventory/department/branch-1001",
)


text = dcc.Markdown(
    """

### Defining the variable in the path

Use the  `path_template` parameter in  `dash.register_page` to define which segments of the path are variables by marking them like this: `<variable_name>`. 
  The layout function then receives the `<variable_name>` as a keyword argument.


The page you are viewing is   `path_variables.py` in the `pages/multi_page_demo` folder.  It's registered like this:

```python


def title(asset_id=None, dept_id=None):
    return f"Asset Analysis: {asset_id}  {dept_id}"


def description(asset_id=None, dept_id=None):
    return f"This is the AVN Industries Asset Analysis: {asset_id} in {dept_id}"


dash.register_page(
    __name__,
    path_template="/asset/<asset_id>/department/<dept_id>",
    title=title,
    description=description,
    path="/asset/inventory/department/branch-1001",
)

```

### Title and Description updated automatically

Note that the title and the description are functions.  This allows you to customize the title and description based on the path. 

In the URL, change inventory or branch to something else and notice the new title.  If you share a link to this
page it will have a customized title and description for this page.  Give it a try!


![image](https://user-images.githubusercontent.com/72614349/154105507-e0fafa2e-11ab-43ac-a4a3-570bf867361a.png)

Note that the layout is also a function.  This is necessary in order to receive the variables passed to the layout.
```

def layout(asset_id=None, dept_id=None, **other_unknown_query_strings):
    return html.Div(        
             f"These variables are passed to the layout from the pathname:  `asset_id: {asset_id} dept_id: {dept_id}`"
           )
    
```
Next: [Query Strings](https://dashlabs.pythonanywhere.com/multi-page-demo/query-string)  Previous [Not Found 404](https://dashlabs.pythonanywhere.com/multi-page-demo/not-found-404)

"""
)


def layout(asset_id=None, dept_id=None, **other_unknown_query_strings):
    text2 = dedent(
    """
    ## Path Variables

    #### On this page, the following variables are passed from the URL pathname to the layout:
    - `asset_id`:   {asset_id}
    - `dept_id`:  {dept_id}

    Give it a try!  Change the branch number or inventory in the URL and see them updated here.

    """).format(asset_id=asset_id, dept_id=dept_id )

    return html.Div(
        [
            dcc.Markdown(text2),
            text,
        ]
    )
