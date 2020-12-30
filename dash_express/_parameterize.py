from functools import wraps
from dash.dependencies import Output, State, Input
import dash_html_components as html
import dash_core_components as dcc

from dash_express.templates.div import FlatDiv
from dash_express.templates.util import build_id
from dash.development.base_component import Component
from plotly.graph_objs import Figure


class ParameterWrapper:
    def __init__(self, value):
        self.value = value

def state(value):
    return StateParameterWrapper(value)

def fixed(value):
    return FixedParameterWrapper(value)

class FixedParameterWrapper(ParameterWrapper):
    def __init__(self, value):
        super().__init__(value)

class StateParameterWrapper(ParameterWrapper):
    def __init__(self, value):
        super().__init__(value)


def parameterize(app, inputs=None, output=None, state=None, template=None, labels=None, optional=(), manual=False, prevent_initial_call=None):
    """
    Parameterize a function using a
    """
    from dash_express.templates.base import ParameterizeDecorator

    if isinstance(inputs, Component):
        # Wrap scalar input
        inputs = [inputs]

    assert inputs

    if template is None:
        template = FlatDiv()

    if labels is None:
        labels = {}
    elif isinstance(labels, list):
        # Convert to integer dict for processing consistency
        labels = {i: label for i, label in enumerate(labels)}

    if not output:
        output = (html.Div(id=build_id("output-div")), "children")

    # Handle positional index case
    if isinstance(inputs, list):
        # Convert to dict for uniform processing, will get converted back to an *args
        # list later
        map_keyword_args = False
        inputs = {i: pattern for i, pattern in enumerate(inputs)}
    else:
        map_keyword_args = True

    # Merge all parameters specified in the state collection into the input dict,
    # and keep track of the keys that are State in the state_keys set
    if state is None:
        state_keys = set()
    elif isinstance(state, list):
        num_inputs = len(inputs)
        num_state = len(state)
        inputs.update({i + num_inputs: v for i, v in enumerate(state)})
        state_keys = {i + num_inputs for i in range(num_state)}
    elif isinstance(state, dict):
        inputs = dict(inputs, **state)
        state_keys = set(state)
    else:
        raise ValueError("Invalid state")

    param_patterns = {}
    fixed_param_values = {}
    for param_name, param in inputs.items():
        # Replace state wrappers around input values with raw value and add name
        # to state_keys dict
        if isinstance(param, FixedParameterWrapper):
            fixed_param_values[param_name] = param.value
            continue

        if isinstance(param, StateParameterWrapper):
            param = param.value
            state_keys.add(param_name)

        param_patterns[param_name] = param

    if manual:
        state_keys.update(inputs.keys())

    param_dependencies = {}
    param_functions = {}

    # inputs
    for param, pattern in param_patterns.items():
        add_parameter_component(
            param, pattern, param_functions, param_dependencies, labels, optional, template,
            state_keys, manual
        )

    # Build param to index mapping
    num_inputs = int(manual)
    for param, dependencies in param_dependencies.items():
        if dependencies and isinstance(dependencies[0], Input):
            num_inputs += len(dependencies)

    all_inputs = []
    all_state = []
    param_index_mapping = {}
    for param, dependencies in param_dependencies.items():
        if dependencies is None:
            param_index_mapping[param] = ()
            continue
        if isinstance(dependencies[0], Input):
            arg_inds = [i + len(all_inputs) for i in range(len(dependencies))]
            all_inputs.extend(dependencies)
        else:  # State
            arg_inds = [
                i + num_inputs + len(all_state) for i in range(len(dependencies))
            ]
            all_state.extend(dependencies)

        pattern_fn = param_functions[param]
        if pattern_fn is not None:
            # Compute parameter value as function of positional argument values
            param_index_mapping[param] = (pattern_fn, arg_inds)
        elif len(arg_inds) > 1:
            # Pass tuple positional argument values as parameter
            param_index_mapping[param] = arg_inds
        else:
            # Use single positional argument value as parameter
            param_index_mapping[param] = arg_inds[0]

    # State
    if manual:
        # Add compute button input
        button = template.Button(
            children="Update",
            id=build_id(name="update-parameters")
        )
        template.add_component(button, role="input", value_property="n_clicks")
        all_inputs.append(Input(button.id, "n_clicks"))

    # Outputs
    # For now, all output placed as children of Div
    if not isinstance(output, list):
        output = [output]
        scalar_output = True
    else:
        scalar_output = False

    output_dependencies = []
    output_index_mapping = []
    for i, output_el in enumerate(output):
        if isinstance(output_el, Output):
            output_el_deps = [output_el]
        else:
            if isinstance(output_el, tuple):
                output_component, output_property = output_el
            else:
                output_component = output_el
                output_property = "value"

            # Overwrite id
            if getattr(output_component, "id", None) is None:
                component_id = build_id(name=i)
                output_component.id = component_id

            output_el_deps, _ = template.add_component(
                output_component, role="output", value_property=output_property, containered=False
            )

        output_el_inds = [len(output_dependencies) + i for i in range(len(output_el_deps))]
        if len(output_el_inds) > 1:
            output_index_mapping.append(tuple(output_el_inds))
        else:
            output_index_mapping.append(output_el_inds[0])
        output_dependencies.extend(output_el_deps)

    if scalar_output:
        output_dependencies = output_dependencies[0]
        output_index_mapping = output_index_mapping[0]

    def wrapped(fn) -> ParameterizeDecorator:
        # Register callback with output component inference
        if map_keyword_args:
            fn = map_input_kwarg_parameters(fn, param_index_mapping, fixed_param_values)
        else:
            fn = map_input_arg_parameters(fn, param_index_mapping, fixed_param_values)

        fn = map_output_positional_args(fn, output_index_mapping)

        should_infer_output = [isinstance(output_el, html.Div) for output_el in output]
        fn = infer_output_component(fn, template, output_dependencies, should_infer_output)
        template.register_app_callback(
            fn, output_dependencies, all_inputs, all_state,
            prevent_initial_call=prevent_initial_call
        )

        if app is not None:
            template.register_callbacks(app)

        # build TemplateDecorator
        return ParameterizeDecorator(fn, template)

    return wrapped


def add_parameter_component(
        param, pattern, param_functions, param_dependencies, labels, optional, template,
        state, manual
):
    pattern_fn, pattern_inputs = add_param_component_to_template(
        param, pattern, labels, optional, template
    )
    update_param_dependencies(
        param, pattern_inputs, pattern_fn, param_dependencies, param_functions, state, manual
    )


def update_param_dependencies(
        param, pattern_inputs, pattern_fn, param_dependencies, param_functions, state, manual
):
    param_functions[param] = pattern_fn
    # Compute positional indices of this pattern's inputs
    if param in state or manual:
        # This is state
        param_dependencies[param] = [
            State(ip.component_id, ip.component_property) for ip in pattern_inputs
        ]
    else:
        # This is an input
        param_dependencies[param] = pattern_inputs


def add_param_component_to_template(param, pattern, labels, optional, template):
    label = labels.get(param, str(param))
    arg_optional = param in optional
    # Expand tuple of (component, prop_name)
    if isinstance(pattern, list):
        options = pattern
        pattern_inputs, pattern_fn = template.add_dropdown(
            options=options, label=label, name=param, optional=arg_optional
        )
    elif isinstance(pattern, tuple) and pattern and isinstance(pattern[0], Input):
        pattern_inputs, pattern_fn = pattern, None
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
        if getattr(component, "id", None):
            component_id = build_id(name=param)
            component.id = component_id

        pattern_inputs, pattern_fn = template.add_component(
            component, name=param, role="input", label=label, value_property=prop_name,
            optional=arg_optional
        )
    elif isinstance(pattern, tuple):
        if len(pattern) == 0:
            pattern_inputs, pattern_fn = None, None
        else:
            if len(pattern) == 2:
                minimum, maximum = pattern
                step = None
            elif len(pattern) == 3:
                minimum, maximum, step = pattern
            else:
                raise ValueError("Tuple default must have length 2 or 3")

            pattern_inputs, pattern_fn = template.add_slider(
                min=minimum, max=maximum, step=step, label=label, name=param,
                optional=arg_optional
            )
    elif isinstance(pattern, str):
        pattern_inputs, pattern_fn = template.add_input(
            value=pattern, label=label, name=param, optional=arg_optional
        )
    elif isinstance(pattern, bool):
        pattern_inputs, pattern_fn = template.add_checkbox(
            value=pattern, label=label, name=param, optional=arg_optional
        )
    elif isinstance(pattern, (Input, State)):
        pattern_inputs, pattern_fn = [pattern], None
    elif isinstance(pattern, dict):
        pattern_keys = list(pattern)
        pattern_keys_inputs = {}
        pattern_keys_fns = {}
        for pattern_key, pattern_val in pattern.items():
            pattern_key_fn, pattern_key_inputs = add_param_component_to_template(
                pattern_key, pattern_val, labels, optional, template
            )
            pattern_keys_inputs[pattern_key] = pattern_key_inputs
            pattern_keys_fns[pattern_key] = pattern_key_fn

        # Build flat tuple of input dependencies
        pattern_inputs = tuple([ip for pkip in pattern_keys_inputs.values() for ip in pkip])

        # Build pattern function that maps this tuple back to dict form
        def pattern_fn(*tuple_vals):
            res = {}
            i = 0
            for pattern_key in pattern_keys:
                n = len(pattern_keys_inputs[pattern_key])
                key_vals = tuple_vals[i:i + n]
                i += n

                pattern_key_fn = pattern_keys_fns[pattern_key]
                if pattern_key_fn is not None:
                    key_vals = pattern_key_fn(*key_vals)
                elif len(key_vals) == 1:
                    key_vals = key_vals[0]
                res[pattern_key] = key_vals

            return res
    else:
        raise Exception(f"unknown pattern for {param} with type {type(pattern)}")
    return pattern_fn, pattern_inputs


def map_input_kwarg_parameters(fn, param_index_mapping, fixed_param_values):
    """
    Map keyword arguments
    """
    @wraps(fn)
    def wrapper(*args):
        kwargs = dict(fixed_param_values)
        for param, mapping in param_index_mapping.items():
            if isinstance(mapping, int):
                value = args[mapping]
            elif isinstance(mapping, list):
                value = tuple(args[i] for i in mapping)
            elif isinstance(mapping, tuple):
                if not mapping:
                    value = ()
                else:
                    mapping_fn, arg_indexes = mapping
                    value = mapping_fn(*[args[i] for i in arg_indexes])
            else:
                raise ValueError(f"Unexpected mapping: {mapping}")
            kwargs[param] = value
        return fn(**kwargs)

    return wrapper


def map_input_arg_parameters(fn, param_index_mapping, fixed_param_values):
    """
    Map positional arguments
    """
    @wraps(fn)
    def wrapper(*args):
        num_args = len(param_index_mapping) + len(fixed_param_values)
        positional_args = [None for _ in range(num_args)]

        # Add fixed
        for index, value in fixed_param_values.items():
            positional_args[index] = value

        for index, mapping in param_index_mapping.items():
            if index in fixed_param_values:
                value = fixed_param_values[index]
            elif isinstance(mapping, int):
                value = args[mapping]
            elif isinstance(mapping, list):
                value = tuple(args[i] for i in mapping)
            elif isinstance(mapping, tuple):
                mapping_fn, arg_indexes = mapping
                value = mapping_fn(*[args[i] for i in arg_indexes])
            else:
                raise ValueError(f"Unexpected mapping: {mapping}")
            positional_args[index] = value
        return fn(*positional_args)

    return wrapper


def map_output_positional_args(fn, output_index_mapping):
    @wraps(fn)
    def wrapper(*args, **kwargs):
        positional_values = []
        res = fn(*args, **kwargs)
        index_mapping = output_index_mapping

        if isinstance(output_index_mapping, list):
            assert isinstance(res, list) and len(res) == len(output_index_mapping)
            scalar_output = False
        elif isinstance(output_index_mapping, tuple):
            assert isinstance(res, tuple) and len(res) == len(output_index_mapping)
            res = [res]
            index_mapping = [output_index_mapping]
            scalar_output = True
        else:
            res = [res]
            index_mapping = [output_index_mapping]
            scalar_output = True

        for res_el, output_inds in zip(res, index_mapping):
            if isinstance(output_inds, tuple):
                assert isinstance(res_el, tuple) and len(res_el) == len(output_inds)
                positional_values.extend(res_el)
            else:
                positional_values.append(res_el)

        if scalar_output:
            positional_values = positional_values[0]

        return positional_values

    return wrapper


def infer_output_component(fn, template, output_dependencies, should_infer_output):
    @wraps(fn)
    def wrapper(*args, **kwargs):
        if isinstance(output_dependencies, list):
            res = fn(*args, **kwargs)
            if not isinstance(res, list) or len(res) != len(output_dependencies):
                raise ValueError(
                    f"Expected callback output to be length {len(output_dependencies)} list of components"
                )
            for i in range(len(res)):
                # Only infer output components that are being assigned to children
                if should_infer_output[i]:
                    res[i] = infer_component(res[i], template)
        else:
            res = fn(*args, **kwargs)
            if should_infer_output:
                res = infer_component(res, template)
        return res
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

    component_id = build_id(name=name)
    if isinstance(v, Component):
        # Already a component, leave as-is
        v.id = component_id
        return v
    elif isinstance(v, Figure) or (
            isinstance(v, dict) and ("data" in v or "layout" in v)
    ):
        return template.Graph(v, id=component_id)
    elif pd is not None and isinstance(v, pd.DataFrame):
        return template.DataTable(
            id=component_id,
            columns=[{"name": i, "id": i} for i in v.columns],
            data=v.to_dict('records'),
            page_size=15,
        )
    elif isinstance(v, list):
        return html.Div(
            id=component_id,
            children=[infer_component(el, template) for el in v]
        )
    elif isinstance(v, str):
        return dcc.Markdown(v, id=component_id)
    else:
        # Try string representation
        return html.Pre(str(v), id=component_id)
