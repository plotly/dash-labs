---
register_page:
    name: "Reference"
    title: "MarkdownAIO Reference"
    description: "Dash Labs documentation"
    order: 1
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
        dangerously_use_exec=False,
        side_by_side=False,
        code_first=True,
        code_markdown_props={},
        text_markdown_props={},
        clipboard_props={},
        app_div_props={},
    ):
```  
- `filename`(string):
    The path to the markdown file.  


- `scope`(dict):
    Add scope (i.e. variables) to the context in which the code blocks are executed from. When using `app.callback` the `app` must be included.
    scope=dict(app=app)  


- `scope_creep`(boolean; default False):
     Allows variables from one code block to be defined in the next code block.  



- `dash_scope`(boolean; default True):
    If True, the default scope is:
            ```scope = dict(
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
            )```  



- `template_variables` (dict):
    Variable passed to the  jinja templating engine: https://jinja.palletsprojects.com/en/3.0.x/templates/
    This is a way to display dynamic content.  For example:
    `template_variables={‘language’: ‘english’})`
    See the jinja docs for how to use the template variables in the markdown files.
    {% if language == 'english' %} Hello {% elif language == 'french' %} Bonjour {% endif %}`  



- `dangerously_use_exec` (boolean; default False):
    If `True`, code blocks will be executed.  This may also be set within the code block on the same line as the
    fenced code blocks beginning with three backticks.  



- `side_by_side` (boolean; default False):
    If `True`, the code block will be displayed on the left and the app output on the right on large screens.
    If `False`, or on small screens, code block will be displayed on top and the output will be on the bottom.
    This may also be set within the code block on the same line as the fenced code blocks beginning with three backticks.  



- `code_first` (boolean; default True):
    If `True`, the code block will be displayed on the top and output on the bottom (or on the left if side by side).
    This may also be set within the code block on the same line as the fenced code blocks beginning with three backticks.  



- `code` (boolean; default True):
    If `True`, the code block will be displayed.
    This may also be set within the code block on the same line as the fenced code blocks beginning with three backticks.  



- `clipboard` (boolean; default True):
    If `True`, the clipboard will be displayed.
    This may also be set within the code block on the same line as the fenced code blocks beginning with three backticks.  



- `code_markdown_props`(dict; default ):  A dictionary of properties passed into the dcc.Markdown component that
    displays the code blocks. Does not accept user-supplied `id`, `children`, or `dangerously_allow_html` props.
    This may also be set within the code block on the same line as the fenced code blocks beginning with three backticks.  



- `text_markdown_props`(dict; default ):  A dictionary of properties passed into the dcc.Markdown component that  displays the Markdown text other than code blocks. Does not accept user-supplied `id`, `children` props.  


- `clipboard_props`(dict; default ):  A dictionary of properties passed into the dcc.Clipboard component. Does  not accept user-supplied `id`, `content`, 'target_id` props.
    This may also be set within the code block on the same line as the fenced code blocks beginning with three backticks.  


- `app_div_props`(dict; default ):  A dictionary of properties passed into the html.Div component that contains the output of the executed code blocks.  Does not accept user-supplied `id`, `children` props.
    This may also be set within the code block on the same line as the fenced code blocks beginning with three backticks.  

