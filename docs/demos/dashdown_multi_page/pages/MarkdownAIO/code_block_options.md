---
dash.register_page(
    __name__,   
    order=2,
    title="MarkdownAIO Code Block Options",
    description="Dash Labs documentation",
    layout=MarkdownAIO(
        "pages/MarkdownAIO/code_block_options.md",
        exec_code=True
    ),
)

---

# Code Block Options

You may set certain ways for the output to be displayed, such as showing the code and the output side-by-side, or whether
the code will be either executed. This can be set for all the code blocks, or only certain code block.


### Apply to all code blocks
In this example, all the code blocks in the `home.md` file will be displayed side-by-side. and the clipboard icon will
not be displayed.

```python exec-code-false clipboard_props={"className": "d-none"}
MarkdownAIO("home.md", side_by_side=True, clipboard_props={"className": "d-none"})
```

### Apply to certain code blocks

If you have multiple code blocks in the same Markdown file, you can set the display options for each code block by
including the code block option as a comment.  If you include the comment on the same line as the three back ticks
that define the code block, then the comment won't be visible in the app output. 

For example, if you added the comment # side-by-side-true like shown below the code will be displayed beside the output.


```python exec-code-false

`` `python # side-by-side-true


`` `

```

### Display Options

- `exec_code` (boolean; default False):
         If `True`, code blocks will be executed.  This may also be set within the code block with the comment # exec-code-true or # exec-code-false  


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
displays the Markdown text other than code blocks. Does not accept user supplied `id`, `children` props.  


- `clipboard_props`(dict; default ):  A dictionary of properties passed into the dcc.Clipboard component. Does
not accept user supplied `id`, `content`, 'target_id` props.
This may also be set within a code block with the comment # clipboard-props-{...}  


- `app_div_props`(dict; default ):  A dictionary of properties passed into the html.Div component that contains
the output of the executed code blocks.  Does not accept user supplied `id`, `children` props.
This may also be set within a code block with the comment # app-div-props-{...}  


## Examples:

Here is a markdown file that will be used in all the examples:

`sample.md`
```python # exec-code-false
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

app.layout = MarkdownAIO("pages/MarkdownAIO/sample.md", exec_code=True)

if __name__ == "__main__":
    app.run_server()
    
````

----

### Side-by-side
The display options may be changed at the file level.  Now all the code blocks in `sample.md` will be displayed side-by-side with the output:


```python 
from dash import Dash
from dash_labs import MarkdownAIO

app.layout = MarkdownAIO("pages/MarkdownAIO/sample.md", side_by_side=True, exec_code=True)

if __name__ == "__main__":
    app.run_server()
    
    
```

--------

### Code First or Output First

In this example, the output is displayed first, followed by the code.  

```python 
from dash import Dash
from dash_labs import MarkdownAIO

app.layout = MarkdownAIO("pages/MarkdownAIO/sample.md", code_first=False, exec_code=True)

if __name__ == "__main__":
    app.run_server()
    
    
```

-------

### Code on the right or left with side-by-side

Now the code is displayed to the right of the output

```python 
from dash import Dash
from dash_labs import MarkdownAIO

app.layout = MarkdownAIO("pages/MarkdownAIO/sample.md", code_first=False, side_by_side=True, exec_code=True)

if __name__ == "__main__":
    app.run_server()
    
    
```

-----

### Displaying the clipboard

In this output, the copy to clipboard icon does not show in the code block


```python 
from dash import Dash
from dash_labs import MarkdownAIO

app.layout = MarkdownAIO("pages/MarkdownAIO/sample.md", clipboard_props={"className": "d-none"}, side_by_side=True, exec_code=True)

if __name__ == "__main__":
    app.run_server()
    
    
```

-----


### Do not execute the code

Here is how to display the code only


```python 
from dash import Dash
from dash_labs import MarkdownAIO

app.layout = MarkdownAIO("pages/MarkdownAIO/sample.md", exec_code=False)

if __name__ == "__main__":
    app.run_server()
    
    
```
----

### Show the output but do not show the code:

This is ideal for a report or presentation where you do not want to show the code that produces the output.


```python 
from dash import Dash
from dash_labs import MarkdownAIO

app.layout = MarkdownAIO("pages/MarkdownAIO/sample.md", code_markdown_props={"className": "d-none"}, exec_code=True)

if __name__ == "__main__":
    app.run_server()
    
    
```





