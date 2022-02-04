"""
 todo
    - reduce security risk with exec
       - local files only. Ensure that the file is within a certain directory, and by default
       that should be the parent directory of the main app but maybe we could create a way to override that. Similar to /assets?
    - css:
       - create a MarkdownAIO stylesheet?
       - eliminated dbc dependency  (replace Rows and Cols with inline css)
       - document the default style in subcomponents and that user-supplied style will overwrite. Or better yet - use a stylesheet.
    - add props to make it easier to hide codeblocks and clipboard?
    - rewrite the _remove_app_instance() to use the AST module
      - allow for other names other than Dash ie app = DashProxy()
    - any advantage to using jinja's read file function?
    - see todos in pages.py in _register_page_from_markdown_file()
    - add ability to change defaults "globally" so it doesn't have to be done for every instance.
    - Add markdown files to hot reload in dash.  That way users can have the same hot-reloading dev experience when working in markdown
    - if code block is not executed don't register callbacks and layout
    - Need to remove if __name__ == "__main__": ...   from the code blocks?
    - refactor the _update_props function.

"""

from dash import dcc, html, dash_table, Input, Output, State, callback
import re
import ast
import copy
import textwrap
import uuid
import random
from jinja2 import Template
import plotly.express as px
import plotly
import dash_bootstrap_components as dbc
import warnings


def warning_message(message, category, filename, lineno, line=None):
    return f"{category.__name__}:\n {message} \n"


warnings.formatwarning = warning_message


class MarkdownAIO(html.Div):
    def __init__(
        self,
        filename,
        scope=None,
        scope_creep=False,
        dash_scope=True,
        template_variables=None,
        exec=False,
        side_by_side=False,
        code_first=True,
        code_markdown_props={},
        text_markdown_props={},
        clipboard_props={},
        app_div_props={},
    ):
        """
        MarkdownAIO is an All-In-One component to display content of Markdown files with the option to run and/or
         display code blocks.

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
           `{% if language == 'english' %} Hello {% elif language == 'french' %} Bonjour {% endif %}`

        - `exec` (boolean; default False):
           If `True`, code blocks will be executed.  This may also be set within the code block with the comment
            # exec-true or # exec-false

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

        # todo figure out correct path to use.
        path = "pages/"
        from jinja2 import Environment, FileSystemLoader

        try:
            with open(filename) as f:
                md_string = f.read()
        except IOError as error:
            print(f"{error} supplied to MarkdownAIO")
            return

        template = Environment(loader=FileSystemLoader(path)).from_string(md_string)
        md_string = template.render(**(template_variables or {}))

        if md_string.startswith("---"):
            split_frontmatter = re.split(r"(^---[\s\S]*?\n*---)", md_string)
            md_string = split_frontmatter[-1]

        split_md_string = re.split(
            #   r"(```[^`]*```)",  # this one doesn't work if there are docstrings in the codeblock
            r"(```[\s\S]*?\n```)",
            md_string,
        )

        # These subcomponent props may not be user-supplied.  Callbacks are not allowed to update the underlying
        # components so the id is unnecessary.
        # The `children` are read-only and are updated by MarkdownAIO
        prohibited_props = {
            "code_markdown_props": ["id", "children", "dangerously_allow_html"],
            "clipboard_props": ["id", "content", "target_id", "children"],
            "app_div_props": ["id", "children"],
            "text_markdown_props": ["id", "children"],
        }

        # Merge user-supplied properties into default properties
        code_markdown_props = copy.deepcopy(code_markdown_props)
        if "style" not in code_markdown_props:
            code_markdown_props["style"] = {"maxHeight": 700, "overflow": "auto"}

        clipboard_props = copy.deepcopy(clipboard_props)
        if "style" not in clipboard_props:
            clipboard_props["style"] = {
                "right": 0,
                "position": "absolute",
                "top": 0,
                "backgroundColor": "#f6f6f6",
                "color": "#2f3337",
                "padding": "4px"
            }
        app_div_props = copy.deepcopy(app_div_props)
        if "style" not in app_div_props:
            app_div_props["style"] = {
                "maxHeight": 700,
                "overflow": "auto",
                "padding": 10,
                "border": "1px solid rgba(100, 100, 100, 0.4)",
            }

        # These props may be updated in each code block
        props = {
            "code_markdown_props": code_markdown_props,
            "clipboard_props": clipboard_props,
            "app_div_props": app_div_props,
            "side_by_side": side_by_side,
            "code_first": code_first,
            "exec": exec,
        }

        _prohibited_props_check(props, prohibited_props)

        # make a unique id for clipboard
        rd = random.Random(0)
        clipboard_id = str(uuid.UUID(int=rd.randint(0, 2 ** 128)))

        # create layout
        reconstructed = []
        code_block = 0
        for i, section in enumerate(split_md_string):
            if "```" in section:
                code_block += 1
                app_card = ""
                updated_props = _update_props(
                    props, prohibited_props, section, code_block, filename
                )

                code_card = html.Div(
                    [
                        dcc.Markdown(section, **updated_props["code_markdown_props"]),
                        dcc.Clipboard(
                            target_id=f"{clipboard_id}{i}",
                            **updated_props["clipboard_props"],
                        ),
                    ],
                    id=f"{clipboard_id}{i}",
                    style={"position": "relative"},
                )

                if updated_props["exec"]:
                    if "app.callback" in section and "app" not in scope:
                        msg1 = textwrap.dedent(
                            """
                            You must pass your own app object into the scope with scope={'app': app}
                            if code blocks within your markdown file have callbacks.
                            """
                        )
                        msg2 = _get_first_lines(section, code_block, filename)
                        raise Exception(msg1 + msg2)
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
                            div_props=updated_props["app_div_props"],
                        )
                    except Exception as e:
                        msg1 = f"\nError: {e} "
                        msg2 = _get_first_lines(section, code_block, filename)
                        print(msg1 + msg2)
                        pass

                # side by side on large screens
                lg = 6 if updated_props["side_by_side"] else 12
                if updated_props["code_first"]:
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
                    dbc.Row(dbc.Col(dcc.Markdown(section, **text_markdown_props)))
                )
        super().__init__(reconstructed)


def _prohibited_props_check(props, prohibited_props, code_block=None, filename=None):
    """
    certain props may not be updated for security reasons and/or because they are updated by
    the MarkdownAIO component
    """

    for prop in props:
        if isinstance(props[prop], dict):
            for p in props[prop]:
                if p in prohibited_props[prop]:
                    raise Exception(
                        f" The `{p}` prop in `{prop}` may not be user-supplied in MarkdownAIO"
                        + f" see code block# {code_block} in module {filename}"
                        if code_block
                        else ""
                    )


def _run_code(code, scope=None, div_props=None):
    if scope is None:
        scope = {}

    # Replacements to get this working in an `exec` environment:
    # 1) Remove language specifier included at beginning of markdown string

    language = code[:6].lower()
    if language.startswith("python"):
        code = code[6:]
    # 2) Remove the app instance in the code block otherwise app.callbacks don't work
    code = _remove_app_instance(code)

    if "app.layout" in code:
        code = code.replace("app.layout", "layout")
    if "layout" in code:
        exec(code, scope)
        return html.Div(scope["layout"], **div_props)

    else:
        # taken from https://stackoverflow.com/a/39381428
        block = ast.parse(code, mode="exec")
        # assumes last node is an expression
        last = ast.Expression(block.body.pop().value)
        exec(compile(block, "<string>", mode="exec"), scope)
        return html.Div(eval(compile(last, "<string>", mode="eval"), scope))


def _parse_props(component_props, section):
    """
    returns the component property dict specified within a code block.

    For example if this was on the first line of the code block:
       `app-div-props-{"style": {"maxHeight": "800px"}}`
    it would return the dict:
        `{"style": {"maxHeight": "800px"}}`
    """
    p = component_props + "-"
    section_split = section.split(p, 1)[-1]

    # check for matching { {} } to find nested dicts
    matched_paren = 0
    parsed_dict = []
    for i in section_split:
        parsed_dict.append(i)
        if i == "{":
            matched_paren += 1
        if i == "}":
            matched_paren -= 1
        if matched_paren == 0:
            return ast.literal_eval("".join(parsed_dict))


def _update_props(
    props_dict, prohibited_props, section, code_block=None, filename=None
):
    """
    update props that are user-supplied  within a code block
    todo - refactor after deciding on the format of the props in the code block
    """
    props_dict = copy.deepcopy(props_dict)

    for prop in props_dict:
        p = prop.replace("_", "-")

        # boolean props
        if p + "-true" in section:
            props_dict[prop] = True
        elif p + "-false" in section:
            props_dict[prop] = False

        # dict props
        elif p in ["code-markdown-props", "clipboard-props", "app-div-props"]:
            if p + "-" in section:
                parsed_props = _parse_props(p, section)
                _prohibited_props_check(
                    {prop: parsed_props}, prohibited_props, code_block, filename,
                )
                props_dict[prop] = {
                    **props_dict[prop],
                    **parsed_props,
                }
    return props_dict


def _remove_app_instance(code):
    """
    Remove the app instance from a code block otherwise app.callback doesn't work. If `app` is defined locally
    within the code block, then it overrides the `app` passed in to the scope.
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


def _get_first_lines(code, code_block_number, file, lines=8):
    """
    Returns an error message and the first few lines of the code block with the error
    """
    split = code.splitlines()[:lines]
    first_lines_of_code = "\n".join(split)
    msg = textwrap.dedent(
        f"""
        The error occurred in code block number {code_block_number} in filename {file}.
        Here are the first few lines of the code block:        
        """
    )
    return msg + first_lines_of_code + "\n----------"
