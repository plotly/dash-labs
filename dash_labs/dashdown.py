from dash import dcc, html, dash_table, Input, Output, State, callback
import re
import ast
import copy
import textwrap
import uuid
import random
import frontmatter
from jinja2 import Environment, FileSystemLoader
import plotly.express as px
import plotly
import warnings
from .util import _parse_codefence


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
        dangerously_use_exec=False,
        side_by_side=False,
        code_first=True,
        clipboard=True,
        code=True,
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

        - `text_markdown_props`(dict; default ):  A dictionary of properties passed into the dcc.Markdown component that
           displays the Markdown text other than code blocks. Does not accept user-supplied `id`, `children` props.

        - `clipboard_props`(dict; default ):  A dictionary of properties passed into the dcc.Clipboard component. Does
            not accept user-supplied `id`, `content`, 'target_id` props.
            This may also be set within the code block on the same line as the fenced code blocks beginning with three backticks.

        - `app_div_props`(dict; default ):  A dictionary of properties passed into the html.Div component that contains
          the output of the executed code blocks.  Does not accept user-supplied `id`, `children` props.
          This may also be set within the code block on the same line as the fenced code blocks beginning with three backticks.

        """
        try:
            md_page = frontmatter.load(filename)
            md_string = md_page.content
            md_props = md_page.get("MarkdownAIO", {})
        except IOError as error:
            print(f"{error} supplied to MarkdownAIO")
            return
        if md_string == "":
            raise Exception(f"No content in {filename}")

        # Update props from front matter todo omg there has to be a better way to do this!
        scope = md_props.get("scope", scope)
        scope_creep = md_props.get("scope_creep", scope_creep)
        dash_scope = md_props.get("dash_scope", dash_scope)
        template_variables = md_props.get("template_variables", template_variables)
        text_markdown_props = md_props.get("text_markdown_props", text_markdown_props)
        code_markdown_props = md_props.get("code_markdown_props", code_markdown_props)
        clipboard_props = md_props.get("clipboard_props", clipboard_props)
        app_div_props = md_props.get("app_div_props", app_div_props)
        side_by_side = md_props.get("side_by_side", side_by_side)
        code_first = md_props.get("code_first", code_first)
        dangerously_use_exec = md_props.get(
            "dangerously_use_exec", dangerously_use_exec
        )
        code = md_props.get("code", code)
        clipboard = md_props.get("clipboard", clipboard)

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
                **(scope or {}),
            )
        elif not scope:
            scope = {}

        path = ""
        template = Environment(loader=FileSystemLoader(path)).from_string(md_string)
        md_string = template.render(**(template_variables or {}))

        # splits the .md file into text blocks and code blocks
        # todo this splits incorrectly when  ``` are in comments.
        split_md_string = re.split(
            r"(```[\s\S]*?\n```)",
            md_string,
        )

        # These subcomponent props may not be user-supplied.  Callbacks are not allowed to update the underlying
        # components so the id is unnecessary.  `children` are read-only and are updated by MarkdownAIO
        prohibited_props = {
            "code_markdown_props": ["id", "children", "dangerously_allow_html"],
            "clipboard_props": ["id", "content", "target_id", "children"],
            "app_div_props": ["id", "children"],
            "text_markdown_props": ["id", "children"],
        }

        # Merge user-supplied properties into default properties -
        code_markdown_props = copy.deepcopy(code_markdown_props)
        if "className" not in code_markdown_props:
            code_markdown_props["className"] = "maio-code"

        clipboard_props = copy.deepcopy(clipboard_props)
        if "className" not in clipboard_props:
            clipboard_props["className"] = "maio-clipboard"

        app_div_props = copy.deepcopy(app_div_props)
        if "className" not in app_div_props:
            app_div_props["className"] = "maio-app"

        text_markdown_props = copy.deepcopy(text_markdown_props)
        if "className" not in text_markdown_props:
            text_markdown_props = {"className": "maio-text"}

        # These props may be updated in each code block
        props = {
            "code_markdown_props": code_markdown_props,
            "clipboard_props": clipboard_props,
            "app_div_props": app_div_props,
            "side_by_side": side_by_side,
            "code_first": code_first,
            "dangerously_use_exec": dangerously_use_exec,
            "code": code,
            "clipboard": clipboard,
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

                code_card = (
                    html.Div(
                        [
                            dcc.Markdown(
                                section, **updated_props["code_markdown_props"]
                            ),
                            dcc.Clipboard(
                                target_id=f"{clipboard_id}{i}",
                                **updated_props["clipboard_props"],
                            )
                            if updated_props["clipboard"]
                            else None,
                        ],
                        id=f"{clipboard_id}{i}",
                        style={"position": "relative"},
                    )
                    if updated_props["code"]
                    else None
                )

                if updated_props["dangerously_use_exec"]:
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
                        code = section.replace("```", "#")
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

                if updated_props["code_first"]:
                    code_display = [
                        html.Div(code_card),
                        html.Div(app_card),
                    ]
                else:
                    code_display = [
                        html.Div(app_card),
                        html.Div(code_card),
                    ]
                # side-by-side on large screens only
                class_name = (
                    "maio-grid-container" if updated_props["side_by_side"] else None
                )
                reconstructed.append(html.Div(code_display, className=class_name))
            else:
                reconstructed.append(
                    html.Div(dcc.Markdown(section, **text_markdown_props))
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
                if p in prohibited_props.get(prop, []):
                    raise Exception(
                        f" The `{p}` prop in `{prop}` may not be user-supplied in MarkdownAIO"
                        + f" see code block# {code_block} in module {filename}"
                        if code_block
                        else ""
                    )


def _run_code(code, scope=None, div_props=None):
    if scope is None:
        scope = {}

    if "app.layout" in code:
        code = code.replace("app.layout", "layout")
    if "layout" in code:
        # Remove the app instance in the code block otherwise app.callbacks don't work
        tree = ast.parse(code)
        new_tree = RemoveAppAssignment().visit(tree)
        exec(compile(new_tree, filename="<ast>", mode="exec"), scope)

        return html.Div(scope["layout"], **div_props)

    else:
        # taken from https://stackoverflow.com/a/39381428
        block = ast.parse(code, mode="exec")
        # assumes last node is an expression
        last = ast.Expression(block.body.pop().value)
        exec(compile(block, "<string>", mode="exec"), scope)
        return html.Div(
            eval(compile(last, "<string>", mode="eval"), scope), **div_props
        )


def _update_props(
    props_dict, prohibited_props, section, code_block=None, filename=None
):
    """update props that are user-supplied  within a code block"""
    props_dict = copy.deepcopy(props_dict)

    code_fence = section.splitlines()[0]
    try:
        new_props = _parse_codefence(code_fence)
    except Exception as e:
        raise Exception(
            f"\nError in codeblock number: {code_block} in file: {filename} \n {code_fence}\n{e}"
        )

    for p in new_props:
        if p not in props_dict:
            raise Exception(
                f"\nProp `{p}` is not a valid prop or may not be updated in a code block.\nError in codeblock number: {code_block} in file: {filename}"
            )

    _prohibited_props_check(new_props, prohibited_props, code_block, filename)

    try:
        props_dict.update(new_props)
    except Exception as e:
        raise Exception(
            f"\nError in codeblock number: {code_block} in file: {filename} \n{e}"
        )

    return props_dict


def _get_first_lines(code, code_block_number, file, lines=8):
    """
    Returns an error message and the first few lines of the code block
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


class RemoveAppAssignment(ast.NodeTransformer):
    """
    Remove the app instance from a code block otherwise app.callback` doesn't work. If `app` is defined locally
    within the code block, then it overrides the `app` passed in to the scope.
    """

    def visit_Assign(self, node):
        if hasattr(node, "targets") and "app" in [
            n.id for n in node.targets if hasattr(n, "id")
        ]:
            return None
        return node
