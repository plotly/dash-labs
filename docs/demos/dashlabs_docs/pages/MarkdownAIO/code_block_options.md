---
register_page:
    order: 2
    title: "MarkdownAIO Code Block Options"
    description: "Dash Labs documentation"
    image: None

MarkdownAIO:
    dangerously_use_exec: True
---


# Code Block Options

You may control the way the output is displayed, such as showing the code and the output side-by-side, or whether
the code will be executed. This can be set for all the code blocks, or only certain code block.


### Apply to all code blocks
In this example, all the code blocks in the `home.md` file will be displayed side-by-side. and the clipboard icon will
not be displayed.


### Apply to certain code blocks

If you have multiple code blocks in the same Markdown file, you can set the display options for each code block by
including the code block option as a comment.  If you include the comment on the same line as the three back ticks
that define the code block, then the comment won't be visible in the app output. 

For example, if you added the comment # side-by-side-true like shown below the code will be displayed beside the output.


`` `python  side_by_side=True, clipboard=False

`` `


### Display Options

- `dangerously_use_exec` (boolean; default False):
         If `True`, code blocks will be executed.  This may also be set within the code block on the same line as
         code fences. 


- `side_by_side` (boolean; default False):
        If `True`, the code block will be displayed on the left and the app output on the right on large screens.
        If `False`, or on small screens, code block will be displayed on top and the output will be on the bottom.
        This may also be set within the code block with the comment # side-by-side-true or # side-by-side-false.  


- `code_first` (boolean; default True):
        If `True`, the code block will be displayed on the top and output on the bottom (or on the left if side by side).
        This may also be set within the code block with the comment # code-first-true or # code-first-false  


- `code_markdown_props`(dict; default ):  A dictionary of properties passed into the dcc.Markdown component that
displays the code blocks. Does not accept user-supplied `id`, `children`, or `dangerously_allow_html` props.
This may also be set within a code block with the comment # code-markdown-props-{...}  


- `text_markdown_props`(dict; default ):  A dictionary of properties passed into the dcc.Markdown component that 
displays the Markdown text other than code blocks. Does not accept user-supplied `id`, `children` props.  


- `clipboard_props`(dict; default ):  A dictionary of properties passed into the dcc.Clipboard component. Does
not accept user-supplied `id`, `content`, 'target_id` props.
This may also be set within a code block with the comment # clipboard-props-{...}  


- `app_div_props`(dict; default ):  A dictionary of properties passed into the html.Div component that contains
the output of the executed code blocks.  Does not accept user-supplied `id`, `children` props.
This may also be set within a code block with the comment # app-div-props-{...}  


## Examples:

Here is a markdown file that will be used in all the examples:

`sample.md`
```python  dangerously_use_exec=False 
## Sample Markdown File

This is a markdown file with a mix of *text and code*.

`` `python
df = px.data.iris()
fig = px.scatter(df, x="sepal_width", y="sepal_length", color="species")
layout = dcc.Graph(figure=fig)
`` `

```

----

### Default Display Options

Here's a Dash app with the default display options for `MarkdownAIO`

```python 
from dash import Dash
from dash_labs import MarkdownAIO

app.layout = MarkdownAIO("pages/MarkdownAIO/sample.md", dangerously_use_exec=True)

if __name__ == "__main__":
    app.run_server()
    
```



----

### Side-by-side
The display options may be changed at the file level.  Now all the code blocks in `sample.md` will be displayed side-by-side with the output:


```python 
from dash import Dash
from dash_labs import MarkdownAIO

app.layout = MarkdownAIO("pages/MarkdownAIO/sample.md", side_by_side=True, dangerously_use_exec=True)

if __name__ == "__main__":
    app.run_server()
    
    
```

--------

### Code First or Output First

In this example, the output is displayed first, followed by the code.  

```python 
from dash import Dash
from dash_labs import MarkdownAIO

app.layout = MarkdownAIO("pages/MarkdownAIO/sample.md", code_first=False, dangerously_use_exec=True)

if __name__ == "__main__":
    app.run_server()
    
    
```

-------

### Code on the right or left with side-by-side

Now the code is displayed to the right of the output

```python 
from dash import Dash
from dash_labs import MarkdownAIO

app.layout = MarkdownAIO("pages/MarkdownAIO/sample.md", code_first=False, side_by_side=True, dangerously_use_exec=True)

if __name__ == "__main__":
    app.run_server()
    
    
```

-----

### Displaying the clipboard

In this output, the copy to clipboard icon does not show in the code block


```python 
from dash import Dash
from dash_labs import MarkdownAIO

app.layout = MarkdownAIO("pages/MarkdownAIO/sample.md", clipboard=False, side_by_side=True, dangerously_use_exec=True)

if __name__ == "__main__":
    app.run_server()
    
    
```

-----


### Do not execute the code

Here is how to display the code only


```python 
from dash import Dash
from dash_labs import MarkdownAIO

app.layout = MarkdownAIO("pages/MarkdownAIO/sample.md", dangerously_use_exec=False)

if __name__ == "__main__":
    app.run_server()
    
    
```
----

### Show the output but do not show the code:

This is ideal for a report or presentation where you do not want to show the code that produces the output.


```python 
from dash import Dash
from dash_labs import MarkdownAIO

app.layout = MarkdownAIO("pages/MarkdownAIO/sample.md", code=False, dangerously_use_exec=True)

if __name__ == "__main__":
    app.run_server()
    
    
```


### Including Markdown files

As you have seen in the above examples, it's possible to include other Markdown files inside
files that are displayed using `MarkdownAIO`

If your Markdown file has multiple code blocks, and you would like to have different options
for each one, you can include your file like above, or simply like this:

```python  dangerously_use_exec=False   

from dash_labs import MarkdownAIO
MarkdownAIO("pages/MarkdownAIO/sample.md", dangerously_use_exec=False)


```

If the file you are including has all the same defaults, you can also include it like this:

{ % include "pages/MarkdownAIO/sample.md" %}

