from functools import wraps
from dash.dependencies import Input, Output
import dash_html_components as html
import dash_core_components as dcc
from dash_table import DataTable

from dash_express.templates.div import FlatDiv
from dash_express.templates.util import build_component_id
from dash.development.base_component import Component

from plotly.graph_objs import Figure


def parameterize(app, fn, params, template=None, labels=None):
    """
    Parameterize a function using a
    """
    if template is None:
        template = FlatDiv()

    if labels is None:
        labels = {}

    # Let template class configure app
    template.configure_app(app)

    # Build template instance
    template_instance = template.instance()

    param_defaults = {}
    for param_name, param in params.items():
        param_defaults[param_name] = param

    inputs = []
    for arg, pattern in param_defaults.items():
        prop_name = "value"
        label = labels.get(arg, arg)

        # Expand tuple of (component, prop_name)
        if (isinstance(pattern, tuple) and
                len(pattern) == 2 and
                isinstance(pattern[0], Component)):
            pattern, prop_name = pattern

        if isinstance(pattern, list):
            options = pattern
            component_id = template_instance.add_dropdown(
                options=options, label=label, name=arg,
            ).id
        elif isinstance(pattern, tuple):
            if len(pattern) == 2:
                minimum, maximum = pattern
                step = None
            elif len(pattern) == 3:
                minimum, maximum, step = pattern
            else:
                raise ValueError("Tuple default must have length 2 or 3")

            component_id = template_instance.add_slider(
                min=minimum, max=maximum, step=step, label=label, name=arg
            ).id
        elif isinstance(pattern, str):
            component_id = template_instance.add_input(
                value=pattern, label=label, name=arg
            ).id
        elif isinstance(pattern, Component):
            # Overwrite id
            component_id = build_component_id(kind="component", name=arg)
            pattern.id = component_id
            template_instance.add_component(pattern, role="input", label=label)
        else:
            raise Exception(f"unknown pattern for {arg} with type {type(pattern)}")

        inputs.append(Input(component_id, prop_name))

    # For now, all output placed as children of Div
    template_instance.add_component(html.Div(id="output"), role="output")
    output = Output("output", "children")

    # Register callback with output component inference
    fn = infer_output_component(fn, template)
    app.callback(output, inputs)(fn)

    return template_instance.layout


def infer_component(v, template):
    # Check if pandas is already imported. Do this instead of trying to import so we
    # don't pay the time hit of importing pandas
    import sys
    if "pandas" in sys.modules:
        pd = sys.modules["pandas"]
    else:
        pd = None

    name = "parameterized_output"

    if isinstance(v, Component):
        # Already a component, leave as-is
        v.id = build_component_id(kind="component", name=name)
        return v
    elif isinstance(v, Figure) or (
            isinstance(v, dict) and ("data" in v or "layout" in v)
    ):
        return template.build_graph(v, name=name)
    elif pd is not None and isinstance(v, pd.DataFrame):
        return DataTable(
            id=build_component_id(kind="datatable", name=name),
            columns=[{"name": i, "id": i} for i in v.columns],
            data=v.to_dict('records'),
        )
    elif isinstance(v, list):
        return html.Div(
            id=build_component_id(kind="div", name=name),
            children=[infer_component(el, template) for el in v]
        )
    elif isinstance(v, str):
        return dcc.Markdown(v, id=build_component_id(kind="markdown", name=name))
    else:
        # Try string representation
        return html.Pre(str(v), id=build_component_id(kind="pre", name=name))


def infer_output_component(fn, template):
    @wraps(fn)
    def wrapper(*args, **kwargs):
        res = fn(*args, **kwargs)
        return infer_component(res, template)
    return wrapper
