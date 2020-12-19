from functools import wraps
from dash.dependencies import Output, State, Input
import dash_html_components as html
import dash_core_components as dcc

from dash_express.templates.div import FlatDiv
from dash_express.templates.util import build_component_id, is_component_id
from dash.development.base_component import Component

from plotly.graph_objs import Figure


def parameterize(app, fn, params, template=None, labels=None, optional=(), manual=False):
    """
    Parameterize a function using a
    """
    if template is None:
        template = FlatDiv()

    if labels is None:
        labels = {}

    param_defaults = {}
    for param_name, param in params.items():
        param_defaults[param_name] = param

    all_inputs = []
    all_state = []
    param_index_mapping = {}

    for arg, pattern in param_defaults.items():
        label = labels.get(arg, arg)
        arg_optional = arg in optional

        # Expand tuple of (component, prop_name)
        if isinstance(pattern, list):
            options = pattern
            pattern_inputs, pattern_fn = template.add_dropdown(
                options=options, label=label, name=arg, optional=arg_optional
            )
        elif isinstance(pattern, tuple):
            if len(pattern) == 2:
                minimum, maximum = pattern
                step = None
            elif len(pattern) == 3:
                minimum, maximum, step = pattern
            else:
                raise ValueError("Tuple default must have length 2 or 3")
            pattern_inputs, pattern_fn = template.add_slider(
                min=minimum, max=maximum, step=step, label=label, name=arg, optional=arg_optional
            )
        elif isinstance(pattern, str):
            pattern_inputs, pattern_fn = template.add_input(
                value=pattern, label=label, name=arg, optional=arg_optional
            )
        elif isinstance(pattern, Component) or (
                isinstance(pattern, tuple) and
                len(pattern) == 2 and
                isinstance(pattern[0], Component)
        ):
            if isinstance(pattern, tuple):
                component, prop_name = pattern
            else:
                component, prop_name = pattern, "value"

            # Overwrite id
            if not is_component_id(getattr(component, "id", None)):
                component_id = build_component_id(kind="component", name=arg)
                component.id = component_id

            pattern_inputs, pattern_fn = template.add_component(
                component, role="input", label=label, value_prop=prop_name, optional=arg_optional
            )
        else:
            raise Exception(f"unknown pattern for {arg} with type {type(pattern)}")

        # Compute positional indices of this pattern's inputs
        # Add 1 for manual since that will push inputs down a slot
        input_inds = [i + len(all_inputs) + int(manual) for i in range(len(pattern_inputs))]

        # Update all inputs list
        all_inputs.extend(pattern_inputs)

        # Build mapping from parameter nmae to positional arguments
        if pattern_fn is not None:
            # Compute parameter value as function of positional argument values
            param_index_mapping[arg] = (pattern_fn, input_inds)
        elif len(input_inds) > 1:
            # Pass tuple positional argument values as parameter
            param_index_mapping[arg] = input_inds
        else:
            # Use single positional argument value as parameter
            param_index_mapping[arg] = input_inds[0]

    if manual:
        # Add compute button input
        button = template.Button(
            children="Update",
            id=build_component_id(kind="button", name="update-parameters")
        )
        template.add_component(button, role="input", value_prop="n_clicks")

        # Convert all inputs to state
        all_state = [State(ip.component_id, ip.component_property) for ip in all_inputs]
        all_inputs = [Input(button.id, "n_clicks")]

    # For now, all output placed as children of Div
    template.add_component(html.Div(id="output"), role="output", value_prop="children")
    output = Output("output", "children")

    # Register callback with output component inference
    fn = map_input_parameters(fn, param_index_mapping)
    fn = infer_output_component(fn, template)
    app.callback(output, all_inputs, all_state)(fn)

    return template.build_layout(app)


def map_input_parameters(fn, param_index_mapping):
    @wraps(fn)
    def wrapper(*args):
        kwargs = {}
        for param, mapping in param_index_mapping.items():
            if isinstance(mapping, int):
                value = args[mapping]
            elif isinstance(mapping, list):
                value = tuple(args[i] for i in mapping)
            elif isinstance(mapping, tuple):
                mapping_fn, arg_indexes = mapping
                value = mapping_fn(*[args[i] for i in arg_indexes])
            else:
                raise ValueError(f"Unexpected mapping: {mapping}")
            kwargs[param] = value
        return fn(**kwargs)

    return wrapper


def infer_output_component(fn, template):
    @wraps(fn)
    def wrapper(*args, **kwargs):
        res = fn(*args, **kwargs)
        return infer_component(res, template)
    return wrapper


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
        return template.Graph(v, id=build_component_id(kind="graph", name=name))
    elif pd is not None and isinstance(v, pd.DataFrame):
        return template.DataTable(
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
