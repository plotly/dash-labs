from dash import dcc, html, dash_table, Input, Output, State, callback
import re
import ast
from jinja2 import Template
import plotly.express as px
import plotly
import dash_bootstrap_components as dbc
import warnings


def warning_message(message, category, filename, lineno, line=None):
    return f"{category.__name__}:\n {message} \n"


warnings.formatwarning = warning_message


"""
 todo 
    - security risk with exec 
       - local files only.  
       ensure that the file is within a certain directory, and by default 
       that should be the parent directory of the main app but maybe we could create a way to override that.
        (and if so, use the new path as the base path for dashdown to look in?)  Similar to /assets?   
    
    - eliminated dbc dependency  (just need to replace Rows and Cols with inline css)   
       - create a dashdown stylesheet?
       
    - rewrite the remove_app_instance() to use the AST module
    
    - any advantage to using jinja's read file function?
    
     - see todos in pages.py in _register_page_from_markdown_file()
     
     - add `dangerously_allow_html` parameter for the dcc.Markdown() in dashdown?
     
     - be able to change `dashdown` default "globally" so it doesn't have to be done for every instance. 
       This would be good especially good for style and className params, and scope.  Currently to add to scope,
       in a multi-page app it's necessary to call dash.register_page from the main app.py file
       
"""


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
    """
    dashdown displays content of a markdown file with the option to run and/or display code blocks.

    - `filename`(string):
       The path to the markdown file.

    - `scope`(dict):
       Add scope to the code blocks. When using `app.callback` the `app` must be included.
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
       `{% if language == 'english' %} Hello {% elif language == 'french' %} Bonjour {% endif %}`

    - `display_code` (boolean; default True):
       If `True`, code blocks will be displayed. This may also be set within the code block with the comment
        # display-code-true or # display-code-false.

    - `exec_code` (boolean; default True):
       If `True`, code blocks will be executed.  This may also be set within the code block with the comment
        # exec-code-true or # exec-code-false

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
      default: {"maxHeight": 700, "overflow": "auto"}

    - `code_className` (string; optional):
      The className of the code display container (Div).

    - `app_style` (dict; optional):
      The style of the app output container (Div).
      default: {"maxHeight": 700, "overflow": "auto"}

    - `app_className` (string; optional):
      The className of the app output container (Div).

    - `text_style` (dict; optional):
      The style of the Narkdown text container (Div).

    - `text_className` (string; optional):
      The className of the Markdown text container (Div)

    """
    if dash_scope:
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
    elif not scope:
        scope = {}

    try:
        with open(filename, "r") as f:
            notebook = f.read()
    except IOError as error:
        warnings.warn(f"{error} supplied to dashdown", stacklevel=2)
        return ""

    # remove frontmatter which is delimited with 3 dashes
    split_frontmatter = re.split(r"(^---[\s\S]*?\n*---)", notebook)
    notebook = split_frontmatter[-1]
    template = Template(notebook)
    notebook = template.render(**(template_variables or {}))

    split_notebook = re.split(
        #   r"(```[^`]*```)",  # this one doesn't work if there are docstrings in the codeblock
        r"(```[\s\S]*?\n```)",
        notebook,
    )

    # make a unique id for clipboard based on the markdown filename
    # todo use UUID here?
    clipboard_id = filename.split(".")[0].replace("\\", "/").replace("/", "-")

    file_display_options = {
        "display_code": display_code,
        "clipboard": clipboard,
        "side_by_side": side_by_side,
        "code_first": code_first,
        "exec_code": exec_code,
    }

    reconstructed = []
    code_block = 0
    for i, section in enumerate(split_notebook):
        if "```" in section:
            code_block += 1
            app_card = ""
            code_card = ""
            display_options = update_display_options(file_display_options, section)

            if display_options["display_code"]:
                if display_options["clipboard"]:
                    code_card = html.Div(
                        html.Div(
                            [
                                dcc.Markdown(
                                    section,
                                    style={"maxHeight": 700, "overflow": "auto"}
                                    if code_style is None
                                    else code_style,
                                    className=code_className,
                                ),
                                dcc.Clipboard(
                                    target_id=f"{clipboard_id}{i}",
                                    style={
                                        "right": 15,
                                        "position": "absolute",
                                        "top": 0,
                                    },
                                ),
                            ],
                            id=f"{clipboard_id}{i}",
                            style={"position": "relative"},
                        ),
                    )
                else:
                    code_card = (
                        dcc.Markdown(
                            section,
                            style={"maxHeight": 700, "overflow": "auto"}
                            if code_style is None
                            else code_style,
                            className=code_className,
                        ),
                    )

            if display_options["exec_code"]:
                if "app.callback" in section and "app" not in scope:
                    raise Exception(
                        """
                        You must pass your own app object into the scope
                        with scope={'app': app} if using callbacks.
                        """
                    )
                if not scope_creep:
                    # make a copy
                    code_scope = dict(**scope)
                else:
                    # use the same dict that'll keep getting mutated
                    code_scope = scope
                try:
                    code = section.replace("```python", "").replace("```", "")
                    app_card = _run_code(
                        code,
                        scope=code_scope,
                        style=app_style,
                        className=app_className,
                    )
                except Exception as e:
                    print(
                        f"""
                    The following error was generated while attempting to execute 
                    code block #: {code_block} in file: {filename}
                    error:  {e}                    
                    """
                    )
                    pass

            # side by side on large screens
            lg = 6 if display_options["side_by_side"] else 12
            if display_options["code_first"]:
                code_display = [
                    dbc.Col(code_card, width=12, lg=lg),
                    dbc.Col(app_card, width=12, lg=lg),
                ]
            else:
                code_display = [
                    dbc.Col(app_card, width=12, lg=lg),
                    dbc.Col(code_card, width=12, lg=lg),
                ]

            reconstructed.append(dbc.Row(code_display))
        else:
            reconstructed.append(
                dbc.Row(
                    dbc.Col(
                        dcc.Markdown(
                            section, style=text_style, className=text_className
                        )
                    )
                )
            )

    return html.Div(reconstructed)


def _run_code(code, scope=None, style=None, className=None):
    if scope is None:
        scope = {}

    # Replacements to get this working in an `exec` environment:
    # 1) Remove language specifier included at beginning of markdown string
    if code.startswith("python"):
        code = code[6:]

    # # 2) Avoid "builtins" error - https://stackoverflow.com/a/49426867
    #      This step is unnecessary if using remove_app_instance()
    # code = code.replace("Dash(__name__)", "Dash()")
    # code = code.replace("Dash(__name__,", "Dash(")

    # 3) Remove the app instance in the code block otherwise app.callbacks don't work
    code = remove_app_instance(code)

    if "app.layout" in code:
        code = code.replace("app.layout", "layout")
    if "layout" in code:
        exec(code, scope)
        style = (
            {
                "maxHeight": 700,
                "overflow": "auto",
                "padding": 10,
                "border": "1px solid rgba(100, 100, 100, 0.4)",
            }
            if style is None
            else style
        )
        return html.Div(scope["layout"], style=style, className=className)

    else:
        # taken from https://stackoverflow.com/a/39381428
        block = ast.parse(code, mode="exec")
        # assumes last node is an expression
        last = ast.Expression(block.body.pop().value)
        exec(compile(block, "<string>", mode="exec"), scope)
        return html.Div(eval(compile(last, "<string>", mode="eval"), scope))


def update_display_options(options_dict, section):
    """
    update file level options with the options specified within the code block
    """
    options = options_dict.copy()
    if "display-code-true" in section:
        options["display_code"] = True
    if "display-code-false" in section:
        options["display_code"] = False
    if "clipboard-true" in section:
        options["clipboard"] = True
    if "clipboard-false" in section:
        options["clipboard"] = False
    if "side-by-side-true" in section:
        options["side_by_side"] = True
    if "side-by-side-false" in section:
        options["side_by_side"] = False
    if "code-first-true" in section:
        options["code_first"] = True
    if "code-first-false" in section:
        options["code_first"] = False
    if "exec-code-true" in section:
        options["exec_code"] = True
    if "exec-code-false" in section:
        options["exec_code"] = False
    return options


def remove_app_instance(code):
    """
    remove the app instance from a code block otherwise app.callback doesn't work
    todo:  This function is a placeholder. It will fail if there are things like unmatched parens in comments within
           the app instance or spaces between Dash and (  and probably other things too.
           Better to use AST module and delete node with app instance.
    """
    split_code = code.splitlines()
    app_instance = False
    new_code = []
    matched_paren = 0

    for line in split_code:
        if "Dash(" in line:
            app_instance = True
        if app_instance:
            matched_paren += line.count("(") - line.count(")")
            if matched_paren == 0:
                app_instance = False
        else:
            new_code.append(line)
    return "\n".join(new_code)
