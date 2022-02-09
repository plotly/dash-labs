---
register_page:   
    name: "Overview"
    title: "MarkdownAIO Overview"
    description: "Dash Labs documentation"
    order: 0

MarkdownAIO:
    side_by_side: True
    dangerously_use_exec: True       

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
app = Dash(__name__)

graph = dcc.Graph()
label = html.P("Petal Width:")
slider = dcc.RangeSlider(0, 2.5, 0.1, marks={0: '0', 2.5: '2.5'}, value=[0.5, 2])

app.layout = html.Div([graph, label, slider])


@callback(Output(graph, "figure"), Input(slider, "value"))
def update_bar_chart(slider_range):
    low, high = slider_range
    mask = (df["petal_width"] > low) & (df["petal_width"] < high)
    return px.scatter(
        df[mask],
        x="sepal_width",
        y="sepal_length",
        color="species",
        size="petal_length",
    )


if __name__ == "__main__":
    app.run_server(debug=True)


```
-----------


### Quickstart  


#### Single Page App  

Here's a single page app made from a Markdown file using `MarkdownAIO`. 


```python dangerously_use_exec=False, side_by_side=False
from dash import Dash
from dash_labs import MarkdownAIO

app.layout = MarkdownAIO("path_to_my_markdown_file.md", dangerously_use_exec=True)

if __name__ == "__main__":
    app.run_server()
    
    
```
-----------

#### Multi Page App

See more information on creating multi-page apps with `pages/` [here]()

Place your Markdown files in the `pages/` folder.  Register the page in one of two ways: 

1) include dash.register_page from a `.py` file and use `MarkdownAIO` to create the layout:

`app.py`
```python dangerously_use_exec=False,  side_by_side=False, clipboard=False
dash.register_page("pages.home", path="/", layout=MarkdownAIO("pages/home.md", dangerously_use_exec=True))
```

2) Include the `dash.register_page` as "front matter" at the top of the Markdown file with the page content.

The front matter is in a yaml format and must be the first thing in the file and must be set between triple-dashed lines. 


`pages/home.md`
```text dangerously_use_exec=False, side_by_side=False, clipboard=False
---
register_page:
    path: "/"   
    
MarkdownAIO:
   dangerously_use_exec: True
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

- By default, the embedded code will not be executed.  The `dangerously_use_exec` prop must be set to `True` for the code to run.


### More on Writing Secure Dash apps with MarkdownAIO

`dangerously_use_exec=True` is only safe when you “trust” the file.  “trust” means that there is no possibility that the file could contain malicious code.
This often means that you wrote the file, the file was not generated dynamically, and no variables are passed into the file.  


It is only safe to pass variables into the file when you “trust” those variables. Meaning
there is no possibility that that variable could come from malicious user or contain malicious content.
This often means that you wrote each of the variables yourself and that they do not come from any other source like an API, database, CSV, dataset.
If your markdown files are created dynamically with variables from other sources, then a malicious user might be able to include malicious data in those sources, which your file would read and then execute directly.


#### Example 1 - Safe: Handwritten Markdown Files

`MarkdownAIO` was intended for documentation purposes where you
handwrite every single file and the files are not generated dynamically.
You are aware of the code that is being exec’d just like you are aware
of the Python code that you’re running.
You are not creating these files dynamically or injecting any variables in them. There is no way that the file could be modified with unsafe code.

##### Example 2 - Unsafe: Creating Reports from CSV Files

Consider an example where your report pulls “biographies” from a CSV file and then creates Markdown files with those biographies embedded in the report.
Consider where you get your CSV from. 

- Is there any possibility that a malicious user could pass a CSV file into your program with a dcc.Upload file, email you or your colleague a CSV file, upload a CSV file to an online forum?

- Was the CSV file created from a database? If so, what website is behind the database and does it allow users to save data? If so, then a malicious user could use that website, save malicious code in the “biography” settings page of the website, and that malicious code would run when MarkdownAIO exec’s the report that was dynamically created with this Biography.


To learn more about creating secure Dash apps, please see [this discussion](https://community.plotly.com/t/writing-secure-dash-apps-community-thread/54619/)
on the Dash community forum.


### Limitations

- `MarkdownAIO` contains no pattern-matching callbacks. So it ***does not*** slow down your app if you have 100+ components
per the limitation described in the [AIO documentation.](https://dash.plotly.com/all-in-one-components#all-in-one-component-limitations).

### Tips

Every `id` in the entire app must be unique.  Even though the example apps can look like stand-alone apps,
under the covers, `MarkdownAIO` creates a multi-page app.  It's a Dash requirement
that all id's in a multi-page are unique.

### Next 

See the reference section and the other examples for more information about all the available options.
