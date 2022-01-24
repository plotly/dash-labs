---
dash.register_page(
    __name__,
    name="Reference",
    order=1,
    layout=dashdown(
        "pages/dashdown/reference.md",
        exec_code=False,
    ),
)
---


# Dashdown Reference


`dashdown` displays content of a markdown file with the option to run and/or display code blocks.


```
def dashdown(
    filename,
    scope=None,
    scope_creep=False,
    dash_scope=True,
    display_code=True,
    exec_code=True,
    template_variables=None,
    side_by_side=False,
    clipboard=True,
    code_first=True,
    code_style=None,
    code_className=None,
    app_style=None,
    app_className=None,
    text_style=None,
    text_className=None,
):
```
    
- `filename`(string):
The path to the markdown file.

- `scope`(dict):
Add scope to the code blocks. When using `app.callback` the `app` must be included. `scope=dict(app=app)`

- `scope_creep`(boolean; default False):
Allows variables from one code block to be defined in the next code block.

- `dash_scope`(boolean; default True):
If True, the default scope is:
    scope = dict(
              dcc=dcc,
              html=html,
              Input=Input,
              Output=Output,
              State=State,
              dash_table=dash_table,
              px=px,
              plotly=plotly,
              dbc=dbc,
              **(scope or {}))

- `template_variables` (dict):
Variable passed to the  jinja templating engine: https://jinja.palletsprojects.com/en/3.0.x/templates/
This is a way to display dynamic content.  For example:
`template_variables={‘language’: ‘english’})`
See the jinja docs for how to use the template variables in the markdown files.
`{% if language == 'english' %} Hello {% elif language == 'french' %} Bonjour {% endif %}`

- `display_code` (boolean; default True):
If `True`, code blocks will be displayed. This may also be set within the code block with the comment # display-code-true or # display-code-false.

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

- `code_style` (dict; optional):
The style of the code display container (Div).
default: {"maxHeight": 600, "overflow": "auto"}

- `code_className` (string; optional):
The className of the code display container (Div).

- `app_style` (dict; optional):
The style of the app output container (Div).
default: {"maxHeight": 700, "overflow": "auto"}

- `app_className` (string; optional):
The className of the app output container (Div).

- `text_style` (dict; optional):
The style of the Markdown text container (Div).

- `text_className` (string; optional):
The className of the Markdown text container (Div)

