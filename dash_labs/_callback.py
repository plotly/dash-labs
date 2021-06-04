from functools import update_wrapper, wraps
from collections import OrderedDict

from dash import exceptions, Dash
from dash.development.base_component import Component
from .dependency import DashLabsDependency, State, Input, Output
from dash_labs.grouping import (
    flatten_grouping,
    make_grouping_by_index,
    validate_grouping,
    map_grouping,
)
from dash.dependencies import (
    Input as Input_dash,
    State as State_dash,
)
import dash_html_components as html

_ALL_DEPS = (Input, Output, State)


class CallbackWrapper:
    """
    Class that functions decorated by app.callback to provide access to
    original function and callback decorator arguments.
    """

    def __init__(
        self,
        fn,
        args_dependencies,
        output_dependencies,
        flat_fn=None,
        flat_output_deps=None,
        flat_input_deps=None,
        flat_state_deps=None,
    ):
        self.fn = fn
        self.args = args_dependencies
        self.output = output_dependencies
        self._flat_fn = flat_fn
        self._flat_output_deps = flat_output_deps
        self._flat_input_deps = flat_input_deps
        self._flat_state_deps = flat_state_deps
        update_wrapper(self, self.fn)

    def __call__(self, *args, **kwargs):
        return self.fn(*args, **kwargs)


def _normalize_inputs(inputs, state, template):
    # Handle positional inputs/state as int dict
    if inputs == [] and isinstance(state, dict):
        inputs = {}

    if not isinstance(inputs, dict):
        input_form = "list"
        if state is not None and isinstance(state, dict):
            raise ValueError("inputs and state must both be lists or dicts")

        if isinstance(inputs, tuple):
            inputs = list(inputs)
        elif not isinstance(inputs, list):
            inputs = [inputs]

        if state:
            if isinstance(state, tuple):
                state = list(state)
            elif not isinstance(state, list):
                state = [state]

        # Create dict from positional argument indices to dependency objects
        # Note that state values always come after inputs in Dash 1
        inputs = {i: val for i, val in enumerate(inputs)}
        num_inputs = len(inputs)
        if state is not None:
            state = {i + num_inputs: val for i, val in enumerate(state)}
    else:  # isinstance(inputs, dict):
        input_form = "dict"

    if state is None:
        state = {}

    # Check for duplicate keys
    dups = [k for k in inputs if k in state]
    if dups:
        raise ValueError(
            "argument names must be unique across input and state\n"
            "    The following were found in both: {dups}".format(dups=dups)
        )

    # Preprocess non-dependency inputs and state into arg instances
    all_inputs = OrderedDict()
    combined_inputs_state = inputs.copy()
    combined_inputs_state.update(state)
    for name, pattern in combined_inputs_state.items():
        if isinstance(pattern, DashLabsDependency) and not pattern.has_component:
            pattern = pattern.dependencies(labs=True)

        flat_deps = flatten_grouping(pattern)
        for dep in flat_deps:
            if not isinstance(dep, DashLabsDependency):
                raise ValueError("Invalid dependency: {}".format(dep))

            if dep.has_component:
                # Apply default label if undefined
                # (if user explicitly set label to None, leave it alone)
                if dep.label is Component.UNDEFINED:
                    dep.label = name

                # Update default location if undefined
                if dep.location is Component.UNDEFINED and template is not None:
                    dep.location = template._default_input_location

        all_inputs[name] = pattern

    return all_inputs, input_form


def _normalize_output(output, template):
    # output_form stores whether wrapped function is expected to return values as
    # scalar, list, or dict.
    output_form = None
    if output is None or isinstance(output, list) and len(output) == 0:
        if template is None:
            raise ValueError(
                "No output dependency objects specified, and no template provided to\n"
                "construct a default output component."
            )
        else:
            output = template.default_output()

    if not isinstance(output, (list, dict)):
        output_form = "scalar"
        output = [output]

    if isinstance(output, list):
        # Convert output from list to
        output = {i: val for i, val in enumerate(output)}
        output_form = output_form or "list"
    else:
        output_form = output_form or "dict"

    all_output = OrderedDict()
    for name, pattern in output.items():
        if isinstance(pattern, DashLabsDependency) and not pattern.has_component:
            pattern = pattern.dependencies(labs=True)

        flat_deps = flatten_grouping(pattern)
        for dep in flat_deps:
            if not isinstance(dep, DashLabsDependency):
                raise ValueError("Invalid dependency: {}".format(dep))

            if dep.has_component:
                # Check is arg is holding a pattern
                if dep.label is Component.UNDEFINED:
                    dep.label = None

                if dep.location is Component.UNDEFINED and template is not None:
                    dep.location = template._default_output_location

        all_output[name] = pattern

    return all_output, output_form


def _add_arg_components_to_template(vals, template):
    for name, val in vals.items():
        deps = flatten_grouping(val)
        for dep in deps:
            if dep.has_component:
                opts = {}
                if isinstance(name, str):
                    opts["name"] = name

                template.add_component(
                    component=dep.component_id,
                    component_property=dep.component_property,
                    location=dep.location,
                    label=dep.label,
                    label_id=dep.label_id,
                    **opts,
                )


def _get_arg_input_state_dependencies(all_inputs):
    input_groupings = OrderedDict()
    input_deps = []
    state_deps = []

    # Collect input groupings
    for name, val in all_inputs.items():
        if isinstance(val, Input):
            grouping = val.dependencies()
            flat_dependencies = val.flat_dependencies()
        else:
            flat_dependencies = [d.dependencies() for d in flatten_grouping(val)]
            if flat_dependencies and isinstance(flat_dependencies[0], Input_dash):
                grouping = val
            else:
                continue
        slc = slice(len(input_deps), len(input_deps) + len(flat_dependencies))
        input_groupings[name] = (grouping, slc)
        input_deps.extend(flat_dependencies)

    # Process state
    num_inputs = len(input_deps)
    for name, val in all_inputs.items():
        if isinstance(val, State):
            grouping = val.dependencies()
            flat_dependencies = val.flat_dependencies()
        else:
            flat_dependencies = [d.dependencies() for d in flatten_grouping(val)]
            if not flat_dependencies or isinstance(flat_dependencies[0], State_dash):
                grouping = val
            else:
                continue

        slc = slice(
            num_inputs + len(state_deps),
            num_inputs + len(state_deps) + len(flat_dependencies),
        )
        input_groupings[name] = (grouping, slc)
        state_deps.extend(flat_dependencies)

    return input_groupings, input_deps, state_deps


def _get_arg_output_dependencies(all_outputs):
    output_groupings = OrderedDict()
    output_deps = []

    # Collect input groupings
    for name, val in all_outputs.items():
        if isinstance(val, Output):
            grouping = val.dependencies()
            flat_dependencies = val.flat_dependencies()
        else:
            grouping = val
            flat_dependencies = [d.dependencies() for d in flatten_grouping(val)]

        output_groupings[name] = grouping
        output_deps.extend(flat_dependencies)

    return output_groupings, output_deps


def callback(app, *args, **kwargs):
    return _callback(
        app, *args, **kwargs, _wrapped_callback=getattr(Dash, "_wrapped_callback", None)
    )


def _callback(
    app,
    *_args,
    **_kwargs,
):
    """
    Implementation of the dash-labs app.callback
    """
    # Parse input arguments in a way that is consistent with Dash 1 app.callback
    # Note that the args argument to app.callback is merged with inputs
    (
        output,
        inputs,
        state,
        prevent_initial_callbacks,
        template,
        _wrapped_callback,
    ) = handle_callback_args(_args, _kwargs)

    # Combine inputs and stated and normalize into an OrderedDict. List/tuple inputs
    # have integer keys, which dict inputs have keyword argument names as keys.
    all_inputs, input_form = _normalize_inputs(inputs, state, template)

    # Likewise, normalize outputs into an OrderedDict
    all_outputs, output_form = _normalize_output(output, template)

    # For dependencies wrapping component instances, add component to template
    if template is not None:
        _add_arg_components_to_template(all_inputs, template)
        _add_arg_components_to_template(all_outputs, template)

    # Compute Dash 1 compatible Input/State dependency lists and argument groupings
    input_groupings, input_deps, state_deps = _get_arg_input_state_dependencies(
        all_inputs
    )

    # Compute Dash 1 compatible Output dependency list and output groupings
    output_groupings, output_deps = _get_arg_output_dependencies(all_outputs)

    def wrapped(fn) -> CallbackWrapper:
        # Preprocess arguments to callback function to create expected argument
        # groupings from the Dash 1 flat input arguments
        callback_fn = map_input_arguments(fn, input_groupings, input_form)

        # Postprocess return value of wrapped function to validate returned groupings
        # and flatten values into linear list expected by Dash 1 callback
        callback_fn = map_output_arguments(
            callback_fn,
            output_groupings,
            output_form,
        )

        # Register wrapped function with app.callback
        if _wrapped_callback is None:
            _callback = Dash.callback
        else:
            _callback = _wrapped_callback

        # Install callback
        if input_deps:
            _callback(
                app,
                output_deps,
                input_deps,
                state_deps,
                prevent_initial_call=prevent_initial_callbacks,
            )(callback_fn)

        # Return CallbackWrapper instance that mimicks wrapped function while providing
        # access to additional metadata about the callback.
        return CallbackWrapper(
            fn,
            all_inputs,
            all_outputs,
            callback_fn,
            output_deps,
            input_deps,
            state_deps,
        )

    return wrapped


def map_input_arguments(fn, input_groupings, input_form):
    @wraps(fn)
    def wrapper(*args):
        # args are the flat list of positional arguments passed to function by
        # app.callback

        expected_num_args = max([slc.stop for _, slc in input_groupings.values()])
        if len(args) != expected_num_args:
            # Not an error condition a user should reach since we control args and
            # input groupings
            raise ValueError(
                "Expected {} input value(s), received {}".format(
                    expected_num_args, len(args)
                )
            )

        fn_kwargs = {}
        for name, (grouping, slc) in input_groupings.items():
            fn_kwargs[name] = make_grouping_by_index(grouping, list(args[slc]))

        if input_form == "list":
            # keys of fn_kwargs are integers and we need to build list of position
            # arguments for fn
            fn_args = [None for _ in fn_kwargs]
            for i, val in fn_kwargs.items():
                fn_args[i] = val
            return fn(*fn_args)
        elif input_form == "scalar":
            return fn(fn_kwargs[0])
        else:  # "dict"
            return fn(**fn_kwargs)

    return wrapper


def map_output_arguments(fn, dep_groupings, output_form):
    @wraps(fn)
    def wrapper(*args, **kwargs):
        res = fn(*args, **kwargs)
        output = []

        if output_form == "scalar":
            dep_grouping = dep_groupings[0]
            if isinstance(dep_grouping, tuple) and isinstance(res, list):
                # Accept list when expecting a tuple
                res = tuple(res)

            flat_res = extract_and_validate_output_values(res, dep_grouping)
            output.extend(flat_res)
        elif output_form == "list":
            if isinstance(res, tuple):
                # Accept tuple when expecting a list
                res = list(res)

            assert isinstance(res, list)
            assert len(res) == len(dep_groupings)

            for i in range(len(dep_groupings)):
                flat_res = extract_and_validate_output_values(res[i], dep_groupings[i])
                output.extend(flat_res)
        else:  # form == "dict"
            assert isinstance(res, dict)
            assert set(res) == set(dep_groupings)

            for name, grouping in dep_groupings.items():
                flat_res = extract_and_validate_output_values(
                    res[name], dep_groupings[name]
                )
                output.extend(flat_res)

        # The return value is the flat list of output arguments returned by the
        # function registered with app.callback
        return output

    return wrapper


def extract_and_validate_output_values(res_grouping, dep_grouping):
    # Extracting property values from dependency components
    if isinstance(res_grouping, DashLabsDependency):
        res_grouping = res_grouping.property_value()

    # Check value against schema
    validate_grouping(res_grouping, dep_grouping)
    flat_results = flatten_grouping(res_grouping, dep_grouping)

    return flat_results


def _validate_prop_name(component, prop_name):
    if (
        isinstance(prop_name, str)
        and prop_name.isidentifier()
        and prop_name in component._prop_names
    ):
        pass
    else:
        raise ValueError(
            "Invalid property {prop} received for component of type {typ}\n".format(
                prop=repr(prop_name), typ=type(component)
            )
        )


def _validate_prop_grouping(component, props):
    for prop in flatten_grouping(props):
        _validate_prop_name(component, prop)


# Modified Dash Callback Validation logic
# ---------------------------------------
def extract_callback_args(args, kwargs, names, type_):
    """Extract arguments for callback from a name and type"""
    parameters = [kwargs[name] for name in names if name in kwargs]

    if parameters:
        if len(parameters) > 1:
            raise ValueError("Only one of input and args may be specified")
        parameters = parameters[0]
        if not isinstance(parameters, (list, tuple, dict)):
            # accept a single item, not wrapped in a list, for any of the
            # categories as a named arg (even though previously only output
            # could be given unwrapped)
            return [parameters]
    else:
        while args and isinstance(args[0], (type_, type_.dependency_class)):
            arg = args.pop(0)
            parameters.append(arg)

    # Convert dash.dependency objects into dash-labs equivalents
    def to_dl(v):
        if isinstance(v, type_.dependency_class):
            return type_(v.component_id, v.component_property)
        else:
            return v

    if isinstance(parameters, list):
        parameters = [map_grouping(to_dl, p) for p in parameters]
    else:
        parameters = map_grouping(to_dl, parameters)

    return parameters


def handle_callback_args(args, kwargs):
    """Split args into outputs, inputs and states"""
    prevent_initial_call = kwargs.get("prevent_initial_call", None)
    if prevent_initial_call is None and args and isinstance(args[-1], bool):
        args, prevent_initial_call = args[:-1], args[-1]

    template = kwargs.get("template", None)
    _wrapped_callback = kwargs.get("_wrapped_callback", None)

    # flatten args, to support the older syntax where outputs, inputs, and states
    # each needed to be in their own list
    flat_args = []
    for arg in args:
        flat_args += arg if isinstance(arg, (list, tuple)) else [arg]

    outputs = extract_callback_args(flat_args, kwargs, ["output"], Output)
    validate_outputs = outputs
    if isinstance(outputs, (list, tuple)) and len(outputs) == 1:
        out0 = kwargs.get("output", args[0] if args else None)
        if not isinstance(out0, (list, tuple, dict)):
            # unless it was explicitly provided as a list, a single output
            # should be unwrapped. That ensures the return value of the
            # callback is also not expected to be wrapped in a list.
            outputs = outputs[0]

    inputs = extract_callback_args(flat_args, kwargs, ["inputs", "args"], Input)
    states = extract_callback_args(flat_args, kwargs, ["state"], State)

    input_values = inputs.values() if isinstance(inputs, dict) else inputs
    state_values = states.values() if isinstance(states, dict) else states
    output_values = (
        validate_outputs.values()
        if isinstance(validate_outputs, dict)
        else validate_outputs
    )

    validate_callback(output_values, input_values, state_values, flat_args)

    return outputs, inputs, states, prevent_initial_call, template, _wrapped_callback


def validate_callback(output, inputs, state, extra_args):
    is_multi = isinstance(output, (list, tuple))

    outputs = output if is_multi else [output]

    if extra_args:
        if not isinstance(extra_args[0], _ALL_DEPS):
            raise exceptions.IncorrectTypeException(
                """
                Positional callback arguments must be `Output`, `Input`, or `State` objects,
                optionally wrapped in a list or tuple. We found (possibly after
                unwrapping a list or tuple):
                {}
                """.format(
                    repr(extra_args[0])
                )
            )

        raise exceptions.IncorrectTypeException(
            """
            In a callback definition, you must provide all Outputs first,
            then all Inputs, then all States. After this item:
            {}
            we found this item next:
            {}
            """.format(
                repr((outputs + inputs + state)[-1]), repr(extra_args[0])
            )
        )
