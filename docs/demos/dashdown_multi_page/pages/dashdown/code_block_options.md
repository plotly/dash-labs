---
dash.register_page(
    __name__,   
    order=2,
    layout=dashdown(
        "pages/dashdown/code_block_options.md",
    ),
)

---

# Code Block Options
The following options may be set at the file level or within a code block:

- `display_code` (boolean; default True): If `True`, code blocks will be displayed. This may also be set within the code block with the comment # display-code-true or # display-code-false.

- `exec_code` (boolean; default True):
         If `True`, code blocks will be executed.  This may also be set within the code block with the comment # exec-code-true or # exec-code-false

- `side_by_side` (boolean; default False):
        If `True`, the code block will be displayed on the left and the app output on the right on large screens.
        If `False`, or on small screens, code block will be displayed on top and the output will be on the bottom.
        This may also be set within the code block with the comment # side-by-side-true or # side-by-side-false.

- `code_first` (boolean; default True):
        If `True`, the code block will be displayed on the top and output on the bottom (or on the left if side by side).
        This may also be set within the code block with the comment # code-first-true or # code-first-false

- `clipboard` (boolean: default True);
        If True, the copy to Clipboard icon will display in the code block.  This may also be set within the code block
        with the comment # clipboard-true or # clipboard-false.

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

Here's a Dash app with the default display options for `dashdown`

```python 
from dash import Dash
from dash_labs import dashdown

app.layout = dashdown("pages/dashdown/sample.md")

if __name__ == "__main__":
    app.run_server()
    
````

----

### Side-by-side
The display options may be changed at the file level.  Now all the code blocks in `sample.md` will be displayed side-by-side with the output:


```python 
from dash import Dash
from dash_labs import dashdown

app.layout = dashdown("pages/dashdown/sample.md", side_by_side=True)

if __name__ == "__main__":
    app.run_server()
    
    
```

The display options may also be set within the code block in a file. For example, if you added the comment # side-by-side-true
on the same line as the three backticks, then you would see the same output as above with the code and the output side-by-side. 
This allows certain code blocks to be displayed in different ways within the same Markdown file.



```python exec-code-false

## Sample Markdown File

This is a markdown file with a mix of *text and code*.

`` `python # side-by-side-true
df = px.data.iris()
fig = px.scatter(df, x="sepal_width", y="sepal_length", color="species")
layout = dcc.Graph(figure=fig)
`` `

```
--------

### Code First or Output First

In this example, the output is displayed first, followed by the code.  

```python 
from dash import Dash
from dash_labs import dashdown

app.layout = dashdown("pages/dashdown/sample.md", code_first=False)

if __name__ == "__main__":
    app.run_server()
    
    
```

-------

### Code on the right or left with side-by-side

Now the code is displayed to the right of the output

```python 
from dash import Dash
from dash_labs import dashdown

app.layout = dashdown("pages/dashdown/sample.md", code_first=False, side_by_side=True)

if __name__ == "__main__":
    app.run_server()
    
    
```

-----

### Displaying the clipboard

In this output, the copy to clipboard icon does not show in the code block


```python 
from dash import Dash
from dash_labs import dashdown

app.layout = dashdown("pages/dashdown/sample.md", clipboard=False, side_by_side=True)

if __name__ == "__main__":
    app.run_server()
    
    
```

-----


### Do not execute the code

Here is how to display the code only


```python 
from dash import Dash
from dash_labs import dashdown

app.layout = dashdown("pages/dashdown/sample.md", exec_code=False)

if __name__ == "__main__":
    app.run_server()
    
    
```
----

### Show the output but do not show the code:

This is ideal for a report or presentation where you do not want to show the code that produces the output.


```python 
from dash import Dash
from dash_labs import dashdown

app.layout = dashdown("pages/dashdown/sample.md", display_code=False)

if __name__ == "__main__":
    app.run_server()
    
    
```





