from functools import update_wrapper, wraps
from dataclasses import dataclass
from typing import Any, Union
from collections import OrderedDict

from dash.development.base_component import Component

from dash_express import build_id, ComponentProps
from .templates.base import BaseTemplate
from dash_express.grouping import (
    flatten_grouping, make_grouping_by_position, validate_grouping, grouping_len
)
from dash.dependencies import Input, Output, State
import dash_html_components as html

_ALL_DEPS = (Input, Output, State)


class CallbackWrapper:
    """
    Class that stands in place of a decorated function and contains references to
    a template
    """

    def __init__(
            self,
            fn,
            template,
            flat_fn=None,
            flat_output_deps=None,
            flat_input_deps=None,
            flat_state_deps=None
    ):
        self.fn = fn
        self._template = template
        self._flat_fn = flat_fn
        self._flat_output_deps = flat_output_deps
        self._flat_input_deps = flat_input_deps
        self._flat_state_deps = flat_state_deps
        update_wrapper(self, self.fn)

    def __call__(self, *args, **kwargs):
        if self.fn is None:
            raise ValueError("CallbackComponents instance does not wrap a function")
        return self.fn(*args, **kwargs)

    @property
    def template(self):
        return self._template

    @property
    def roles(self):
        return self.template.roles

    def layout(self, app, full=True):
        """
        Register callbacks and return layout.
        """
        return self.template.layout(app, full=full)


@dataclass
class arg:
    pattern: Any
    label: Union[str, int] = None
    kind: str = "auto"
    role: str = "input"
    id: str = None

    def __post_init__(self):
        # Init id
        if isinstance(self.pattern, ComponentProps):
            self.id = self.pattern.id
        elif isinstance(self.pattern, Component):
            if getattr(self.pattern, "id", None) is None:
                self.pattern.id = build_id()
            self.id = self.pattern.id
        else:
            self.id = build_id()

        # Call component_props to run pattern validation
        if self.component_props() is None:
            raise ValueError("Unsupported component pattern: {}".format(self.pattern))

        # Validate kind
        valid_kinds = ("auto", "input", "state", "output")
        if self.kind not in valid_kinds:
            raise ValueError(
                "Invalid argument kind {kind}\n"
                "    Supported kinds: {valid_kinds}".format(
                    kind=self.kind, valid_kinds=valid_kinds
                )
            )

    def component_props(self, template: BaseTemplate=None):
        if template is None:
            template = BaseTemplate
        return template.infer_input_component_props_from_pattern(self.pattern, id=self.id)

    @property
    def dependencies(self):
        component_props = self.component_props()
        return getattr(component_props, self.kind)

    @property
    def flat_dependencies(self):
        component_props = self.component_props()
        return getattr(component_props, "flat_" + self.kind)

    @property
    def dependencies_len(self):
        component_props = self.component_props()
        return component_props.props_len


def _is_dependency_grouping(val):
    """Determine if input is a grouping of dependency values"""
    flat_vals = flatten_grouping(val)
    # TODO: require all the same dependency type
    return all(isinstance(el, _ALL_DEPS) for el in flat_vals)


def _normalize_inputs(inputs, state):
    # Handle positional inputs/state as int dict
    if not isinstance(inputs, dict):
        input_form = "list"
        if state is not None and isinstance(state, dict):
            raise ValueError("inputs and state must both be lists or dicts")

        if not isinstance(inputs, list):
            inputs = [inputs]
        if state and not isinstance(state, list):
            state = [state]

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
        if _is_dependency_grouping(pattern):
            pass
        elif isinstance(pattern, arg):
            # Set 'auto' kind to 'input' or 'state'
            if pattern.kind == "auto":
                pattern.kind = "state" if name in state else "input"
        else:
            # Wrap pattern in arg
            kind = "state" if name in state else "input"
            pattern = arg(pattern=pattern, label=name, kind=kind, role="input")

        all_inputs[name] = pattern

    return all_inputs, input_form


def _normalize_output(output):
    # output_form stores whether wrapped function is expected to return values as
    # scalar, list, or dict.
    output_form = None
    if output is None:
        output = html.Div(id=build_id("output-div")).props["children"]

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
        if _is_dependency_grouping(pattern):
            # Nothing to do
            pass
        elif isinstance(pattern, arg):
            # Set 'auto' kind to 'output'
            if pattern.kind == "auto":
                pattern.kind = "output"
        else:
            # Wrap pattern in arg
            pattern = arg(pattern=pattern, label=name, kind="output", role="output")

        all_output[name] = pattern

    return all_output, output_form


def _add_arg_components_to_template(vals, template):
    for name, val in vals.items():
        if not isinstance(val, arg):
            continue

        opts = {}
        if isinstance(name, str):
            opts["name"] = name

        component_props = val.component_props(template)
        template.add_component(
                component=component_props.component,
                value_property=component_props.props,
                role=val.role,
                label=val.label,
                **opts
        )

def _get_arg_input_state_dependencies(all_inputs):
    input_groupings = OrderedDict()
    input_deps = []
    state_deps = []

    # Collect input groupings
    for name, val in all_inputs.items():
        if isinstance(val, arg) and val.kind == "input":
            grouping = val.dependencies
            flat_dependencies = val.flat_dependencies
        else:
            flat_dependencies = flatten_grouping(val)
            if flat_dependencies and isinstance(flat_dependencies[0], Input):
                grouping = val
            else:
                continue
        slc = slice(len(input_deps), len(input_deps) + len(flat_dependencies))
        input_groupings[name] = (grouping, slc)
        input_deps.extend(flat_dependencies)

    # Process state
    num_inputs = len(input_deps)
    for name, val in all_inputs.items():
        if isinstance(val, arg) and val.kind == "state":
            grouping = val.dependencies
            flat_dependencies = val.flat_dependencies
        else:
            flat_dependencies = flatten_grouping(val)
            if not flat_dependencies or isinstance(flat_dependencies[0], State):
                grouping = val
            else:
                continue

        slc = slice(
            num_inputs + len(state_deps),
            num_inputs + len(state_deps) + len(flat_dependencies)
        )
        input_groupings[name] = (grouping, slc)
        state_deps.extend(flat_dependencies)

    return input_groupings, input_deps, state_deps


def _get_arg_output_dependencies(all_outputs):
    output_groupings = OrderedDict()
    output_deps = []

    # Collect input groupings
    for name, val in all_outputs.items():
        if isinstance(val, arg):
            grouping = val.dependencies
            flat_dependencies = val.flat_dependencies
        else:
            grouping = val
            flat_dependencies = flatten_grouping(val)

        output_groupings[name] = grouping
        output_deps.extend(flat_dependencies)

    return output_groupings, output_deps


def callback(
    app,
    # TODO: process *args for loose dependency objects for backward compat
    # *args,
    output=None,
    inputs=None,
    state=None,
    template=None,
    prevent_initial_call=None,
):
    # TODO: default template to FlatDiv
    from dash_express.templates import FlatDiv
    if template is None:
        template =  FlatDiv()

    # Preprocess non-dependency outputs into ComponentPatterns
    all_inputs, input_form = _normalize_inputs(inputs, state)
    all_outputs, output_form = _normalize_output(output)

    # Add constructed/literal components to template
    _add_arg_components_to_template(all_inputs, template)
    _add_arg_components_to_template(all_outputs, template)

    # Compute Input/State dependency lists and argument groupings
    input_groupings, input_deps, state_deps = _get_arg_input_state_dependencies(
        all_inputs
    )

    # Compute Output dependency lists and groupings
    output_groupings, output_deps = _get_arg_output_dependencies(all_outputs)

    def wrapped(fn) -> CallbackWrapper:
        # Register callback with output component inference
        callback_fn = map_input_arguments(fn, input_groupings, input_form)
        callback_fn = map_output_arguments(
            callback_fn, output_groupings, output_form, template
        )

        # Register wrapped function with app.callback
        app.callback(
            output_deps, input_deps, state_deps,
            prevent_initial_call=prevent_initial_call
        )(callback_fn)

        return CallbackWrapper(
            fn, template, callback_fn, output_deps, input_deps, state_deps
        )

    return wrapped


def map_input_arguments(fn, input_groupings, input_form):
    @wraps(fn)
    def wrapper(*args):
        # args are the flat list of positional arguments passed to function by
        # app.callback

        expected_num_args = max([slc.stop for _, slc in input_groupings.values()])
        if len(args) != expected_num_args:
            # TODO: error report numbers not correct with grouped inputs
            # error condition is correct.
            raise ValueError(
                "Expected {} inputs values, received {}".format(
                    expected_num_args, len(args))
            )

        fn_kwargs = {}
        for name, (grouping, slc) in input_groupings.items():
            fn_kwargs[name] = make_grouping_by_position(grouping, list(args[slc]))

        if input_form == "list":
            # keys of fn_kwargs are integers and we need to build list of position
            # arguments for fn
            fn_args = [None for _ in fn_kwargs]
            for i, val in fn_kwargs.items():
                fn_args[i] = val
            return fn(*fn_args)
        elif input_form == "scalar":
            return fn(fn_kwargs[0])
        else: # "dict"
            return fn(**fn_kwargs)

    return wrapper


def map_output_arguments(fn, dep_groupings, output_form, template):
    @wraps(fn)
    def wrapper(*args, **kwargs):
        res = fn(*args, **kwargs)
        output = []

        # Wrap scalar to normalize with list logic path
        if output_form == "scalar":
            res = [res]
            form = "list"
        else:
            form = output_form

        if form == "list":
            assert isinstance(res, list)
            assert len(res) == len(dep_groupings)

            for i in range(len(dep_groupings)):
                flat_res = extract_and_infer_flat_outputs_values(
                    res[i], dep_groupings[i], template
                )
                output.extend(flat_res)
        else:  # form == "dict"
            assert isinstance(res, dict)
            assert set(res) == set(dep_groupings)

            for name, grouping in dep_groupings.items():
                flat_res = extract_and_infer_flat_outputs_values(
                    res[name], dep_groupings[name], template
                )
                output.extend(flat_res)

        # The return value is the flat list of output arguments returned by the
        # function registered with app.callback
        return output

    return wrapper


def extract_and_infer_flat_outputs_values(
        res_grouping, dep_grouping, template
):
    # Check value against schema
    validate_grouping(res_grouping, dep_grouping)
    flat_results = flatten_grouping(res_grouping)
    flat_deps = flatten_grouping(dep_grouping)

    for i, dep in enumerate(flat_deps):
        if dep.component_property == "children":
            flat_results[i] = template.infer_output_component_from_value(
                flat_results[i]
            )

    return flat_results
