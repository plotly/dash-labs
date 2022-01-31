---
dash.register_page(
    __name__,    
    name="Overview",
    title="MarkdownAIO Overview",
    description="Dash Labs documentation",
    order=0,
    layout=MarkdownAIO(
        "pages/MarkdownAIO/overview.md",
        side_by_side=True,  
        exec_code=True,
    ),
   app_className="mb-4",
   text_className="mb-4 pb-4"
)
---

# Dash Labs Top Secret Feature Preview



## Welcome to `MarkdownAIO` -- _Markdown that runs code_ !

-------

### `MarkdownAIO` is ideal for:  

 - __Tutorials__  
Write a tutorial in Markdown and use `MarkdownAIO` to create an interactive app that displays the code and the output.  


 - __Reports__    
Use `MarkdownAIO` to create interactive reports and presentations by displaying the app output and hiding the code blocks.  


 - __Documentation__  
Use `MarkdownAIO` to create interactive documentation.  See the link on the left "deploying a `README.md` with `MarkdownAIO`" to
see the README.md from the `dash-extensions` library.  

 - __Multi-page apps__  
Use `MarkdownAIO` with `pages/` to easily build multi-page apps.  This documentation is written in Markdown and the app
is created with `pages/` and `MarkdownAIO`. You can find the code [here](https://github.com/AnnMarieW/dash-labs/tree/MarkdownAIO/docs/demos/MarkdownAIO_multi_page).  



------------

The page you are now viewing is a Markdown file.  Here's a codeblock included in the file. 
Try moving the sliders  - it's live!


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


### Quickstart  


#### Single Page App  

Here's a single page app made from a Markdown file using `MarkdownAIO`. 


```python exec-code-false side-by-side-false
from dash import Dash
from dash_labs import MarkdownAIO

app.layout = MarkdownAIO("path_to_my_markdown_file.md", exec_code=True)

if __name__ == "__main__":
    app.run_server()
    
    
```
-----------

#### Multi Page App

See more information on creating multi-page apps with `pages/` [here]()

Place your Markdown files in the `pages/` folder.  Register the page in one of two ways: 

1) include dash.register_page from a `.py` file and use `MarkdownAIO` to create the layout:

`app.py`
``` python exec-code-false  side-by-side-false clipboard-props-{"className": "d-none"}
dash.register_page("pages.home", path="/", layout=MarkdownAIO("pages/home.md", exec_code=True))
```

2) Include the `dash.register_page` as "front matter" at the top of the Markdown file with the page content.

The `dash.register_page` must be the first thing in the file and must be set between triple-dashed lines. 

`pages/home.md`
```text exec-code-false side-by-side-false clipboard-props-{"className": "d-none"}
---
dash.register_page(__name__, path="/", layout=MarkdownAIO("pages/home.md", exec_code=True))
---

# My home Page
## This is the rest of my Markdown content for the home page


```

---------
--------

### App Security

`MarkdownAIO` uses `exec` to run the code blocks. Given that `exec` can potentially introduce security
risks, the following measures have been taken to limit the possibility of code being executed from an
unknown or untrustworthy source or from a malicious user at runtime:

- Only filenames can be supplied to `MarkdownAIO`. The file(s) must exist in a known directory on the 
server before the app starts. 

- By default, the files must reside in the parent directory of the main app.  You may specify an alternate
path by... (todo)

- Content in files downloaded by users during runtime cannot be executed.

- External URLs are not a valid file path for the filename passed to `MarkdownAIO`.

- It is not possible pass code directly to `MarkdownAIO`. This eliminates the risk of executing code supplied
by a malicious user at runtime from a callback.

- By default, the embedded code will not be executed.  The `exec_code` prop must be set to `True` for the code to run.


To learn more about creating secure Dash apps, please see [this discussion](https://community.plotly.com/t/writing-secure-dash-apps-community-thread/54619/)
on the Dash community forum.

### Limitations

- `MarkdownAIO` contains no pattern-matching callbacks. So it ***does not*** slow down your app if you have 100+ components
per the limitation described in the [AIO documentation.](https://dash.plotly.com/all-in-one-components#all-in-one-component-limitations).

### Next 


See the reference section and the other examples for more information about all the available options.