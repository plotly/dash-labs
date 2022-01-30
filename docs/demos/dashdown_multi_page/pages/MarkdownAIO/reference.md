---
dash.register_page(
    __name__,
    name="Reference",
    title="MarkdownAIO Reference",
    description="Dash Labs documentation",
    order=1,
    layout=MarkdownAIO(
        "pages/MarkdownAIO/reference.md",
        exec_code=False,
    ),
)
---


# MarkdownAIO Reference


`MarkdownAIO` is an All-In-One component to display content of Markdown files with the option to run and/or display code blocks.

```
class MarkdownAIO(html.Div):
    def __init__(
        self,
        filename,
        scope=None,
        scope_creep=False,
        dash_scope=True,
        template_variables=None,
        exec_code=False,
        side_by_side=False,
        code_first=True,
        code_markdown_props={},
        text_markdown_props={},
        clipboard_props={},
        app_div_props={},
    ):
```  

- `filename`(string):The path to the markdown file.

- `scope`(dict): Add scope to the code blocks. When using `app.callback` the `app` must be included.
           `scope=dict(app=app)`

- `scope_creep`(boolean; default False): Allows variables from one code block to be defined in the next code block.

- `dash_scope`(boolean; default True):
If True, the default scope is:
```
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
  **(scope or {}),
)
```  


- `template_variables` (dict): Variable passed to the  jinja templating engine: https://jinja.palletsprojects.com/en/3.0.x/templates/
This is a way to display dynamic content.  For example:  
`template_variables={‘language’: ‘english’})`
See the jinja docs for how to use the template variables in the markdown files.
`{% if language == 'english' %} Hello {% elif language == 'french' %} Bonjour {% endif %}`  

- `exec_code` (boolean; default False):
If `True`, code blocks will be executed.  This may also be set within the code block with the comment
`# exec-code-true or # exec-code-false ` 

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

