---
dash.register_page(
    __name__,
    path= "/",
    name="Overview",
    order=0,
    layout=dashdown(
        "pages/dashdown/overview.md",
        side_by_side=True,        
    ),
)
---

# Dash Labs Top Secret Feature Preview

-----

## Welcome to `dashdown`! - _Markdown that runs code_
--------------

### Background

`dashdown` displays the text of a Markdown file and  can execute the embedded code blocks.  Now it's possible to write your
page layouts entirely in Markdown. This is convenient when your content is a mix of narrative and code. 

Use `dashdown` to create interactive reports and presentations by displaying the app output and hiding
the code blocks. Use `dashdown` to create interactive documentation by deploying your project's `README.md` file.
You can also use `dashdown` to display content within an app layout as well. This is conveinient when you would like
to display the content from Markdown files in a highly customized Dash app.


 
### `dashdown` is ideal for:  

 - __Reports__  
 - __Presentations__
 - __Documentation__ 
 - __Tutorials__
 

`dashdown` can be used with `pages` to build multi-page apps.  The documentation you are now viewing was created with 
`pages/` and `dashdown`. You can find the code [here]().  See the [multi-page apps]() section for more information on `pages/` and see
the quickstart guide below for how to include `dashdown` in multi-page apps.



------------

### Quickstart  


##### Single Page App

Here a single page app made from a Markdown file using `dashdown`. It's live!  Try interacting with the slider.


```python exec-code-false
from dash import Dash
from dash_labs import dashdown

app.layout = dashdown("path_to_my_markdown_file.md", side_by_side=True)

if __name__ == "__main__":
    app.run_server()
    
    
```
----------
----------
`my_markdown_file.md`
```python

from dash import Dash, dcc, html, Output, Input, callback
import plotly.express as px


df = px.data.iris()
fig = px.scatter(
        df, x="sepal_width", y="sepal_length",
        color="species", size='petal_length',
        hover_data=['petal_width'])
        
app = Dash(__name__)

app.layout = html.Div([
    dcc.Graph(id="scatter-plot"),
    html.P("Petal Width:"),
    dcc.RangeSlider(
        id='range-slider',
        min=0, max=2.5, step=0.1,
        marks={0: '0', 2.5: '2.5'},
        value=[0.5, 2]
    ),
])

@callback(
    Output("scatter-plot", "figure"),
    Input("range-slider", "value"))
def update_bar_chart(slider_range):
    low, high = slider_range
    mask = (df['petal_width'] > low) & (df['petal_width'] < high)
    fig = px.scatter(
        df[mask], x="sepal_width", y="sepal_length",
        color="species", size='petal_length',
        hover_data=['petal_width'])
    return fig

if __name__ == '__main__':
    app.run_server(debug=True)


```
-----------
-----------

#### Multi Page App

See more information on creating multi-page apps with `pages/` [here]()

`dashdown` is compatible with the `pages/` api.  Place your Markdown file in the `pages/` folder.  Then add it to `dash.page_registry`
in one of two ways: 

1) include dash.register_page from a `.py` file and use `dashdown` to create the layout:

`app.py`
``` python exec-code-false clipboard-false
dash.register_page("pages.home", path="/", layout=dashdown("pages/home.md"))
```

2) Include the `dash.register_page()` as "front matter" at the top of the Markdown file with the page content.

The `dash.register_page()` must be the first thing in the file and must be set between triple-dashed lines. 

`pages/home.md`
```text exec-code-false clipboard-false
---
dash.register_page(__name__, path="/", layout=dashdown("pages/home.md"))
---

# My home Page
## This is the rest of my Markdown content for the home page


```

---------
--------

### App Security

`dashdown` uses `exec` to run the code blocks. Given that `exec` can potentially introduce security
risks, the following measures have been taken to limit the possibility of code being executed from an
unknown or untrustworthy source or from a malicious user at runtime:

- Only filenames can be supplied to `dashdown`. The file(s) must exist in a known directory on the 
server before thea app starts. 

- By default, the files must be within the parent directory of the main app.  You may specify an alternate
path by... (todo)

- Content in files downloaded by users during runtime cannot be executed.

- External URL are not a valid file path for the filename passed to `dashdown`.

- It is not possible pass code directly to `dashdown`. This eliminates the risk of executing code supplied
by a malicious user at runtime from a callback.

- The `dangerously_allow_html` is set to `False` for displaying the Markdown text. 

To learn more about creating secure Dash apps, please see [this discussion](https://community.plotly.com/t/writing-secure-dash-apps-community-thread/54619/)
on the Dash community forum.

### Limitations
(todo)

### Next 

See the reference section and the other examples for more information about all the available options.