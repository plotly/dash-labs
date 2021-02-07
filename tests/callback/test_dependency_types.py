import pytest

from dash.dependencies import Input, Output, State
import dash_html_components as html
import dash_core_components as dcc
import datetime

import dash_express as dx

from . import make_deps, mock_fn_with_return, assert_deps_eq
from ..fixtures import (
    app, test_template, tuple_grouping_size, dict_grouping_size, mixed_grouping_size
)
from ..helpers_for_testing import flat_deps


@pytest.mark.parametrize("input_form", [list, tuple])
def test_arg_dependencies(app, test_template, input_form):
    inputs = input_form([
        dx.arg(dcc.Slider(), label="Slider"),
        dx.arg(dcc.Dropdown(), label="Dropdown"),
    ])
    state = dx.arg(dcc.Input(), label="State Input")
    output = dx.arg(dcc.Markdown(), props="children", label="Markdown Output")

    # Build mock function
    fn = mock_fn_with_return("Hello, world")
    fn_wrapper = app.callback(
        output=output, inputs=inputs, state=state, template=test_template
    )(fn)

    # call flat version (like dash would)
    assert fn_wrapper._flat_fn(1, "Option", "Some Text") == ["Hello, world"]

    # Check how mock function was called
    args, kwargs = fn.call_args
    assert args == (1, "Option", "Some Text")
    assert not kwargs

    # Check order of dependencies
    assert_deps_eq(fn_wrapper._flat_input_deps, [a.dependencies for a in inputs])
    assert_deps_eq(fn_wrapper._flat_state_deps, [state.dependencies])
    assert_deps_eq(fn_wrapper._flat_output_deps, [output.dependencies])


def test_scalar_input_arg_dependencies(app, test_template):
    inputs = dx.arg(dcc.DatePickerRange(), props=("start_date", "end_date"))
    state = dx.arg(dcc.Input())
    output = dx.arg(dcc.Markdown(), props="children")

    # Build mock function
    fn = mock_fn_with_return("Hello, world")
    fn_wrapper = app.callback(
        output=output, inputs=inputs, state=state, template=test_template
    )(fn)

    # call flat version (like dash would)
    assert fn_wrapper._flat_fn(
        datetime.date(2010, 1, 1), datetime.date(2010, 1, 10), "Some Text"
    ) == ["Hello, world"]

    # Check how mock function was called
    args, kwargs = fn.call_args
    assert args == ((datetime.date(2010, 1, 1), datetime.date(2010, 1, 10)), "Some Text")
    assert not kwargs

    # Check order of dependencies
    assert_deps_eq(fn_wrapper._flat_input_deps, list(inputs.dependencies))
    assert_deps_eq(fn_wrapper._flat_state_deps, [state.dependencies])
    assert_deps_eq(fn_wrapper._flat_output_deps, [output.dependencies])


def test_scalar_output_arg_dependencies(app, test_template):
    inputs = dx.arg(html.Button(), props="n_clicks")
    state = dx.arg(dcc.Input())
    output = dx.arg(dcc.DatePickerRange(), props=("start_date", "end_date"))

    # Build mock function
    fn = mock_fn_with_return((datetime.date(2010, 1, 1), datetime.date(2010, 1, 10)))
    fn_wrapper = app.callback(
        output=output, inputs=inputs, state=state, template=test_template
    )(fn)

    # call flat version (like dash would)
    assert fn_wrapper._flat_fn(
        12, "Some Text"
    ) == [datetime.date(2010, 1, 1), datetime.date(2010, 1, 10)]

    # Check how mock function was called
    args, kwargs = fn.call_args
    assert args == (12, "Some Text")
    assert not kwargs

    # Check order of dependencies
    assert_deps_eq(fn_wrapper._flat_input_deps, [inputs.dependencies])
    assert_deps_eq(fn_wrapper._flat_state_deps, [state.dependencies])
    assert_deps_eq(fn_wrapper._flat_output_deps, list(output.dependencies))


def test_component_dependencies(app, test_template):
    inputs = [dcc.Slider(), dx.arg(dcc.DatePickerRange(), props=("start_date", "end_date"))]
    state = [dcc.Input()]
    output = dx.arg(dcc.Markdown(), props="children")

    # Build mock function
    fn = mock_fn_with_return("Hello, world")
    fn_wrapper = app.callback(
        output=output, inputs=inputs, state=state, template=test_template
    )(fn)

    # call flat version (like dash would)
    assert fn_wrapper._flat_fn(1, datetime.date(2010, 1, 1), datetime.date(2010, 1, 10), "Some Text") == ["Hello, world"]

    # Check how mock function was called
    args, kwargs = fn.call_args
    assert args == (1, (datetime.date(2010, 1, 1), datetime.date(2010, 1, 10)), "Some Text")
    assert not kwargs

    # Check order of dependencies
    assert_deps_eq(
        fn_wrapper._flat_input_deps,
        [Input(inputs[0].id, "value"), Input(inputs[1].id, "start_date"), Input(inputs[1].id, "end_date")]
    )
    assert_deps_eq(
        fn_wrapper._flat_state_deps, [State(state[0].id, "value")]
    )
    assert_deps_eq(fn_wrapper._flat_output_deps, [output.dependencies])

    # Check dependencies
    # Slider
    input_param_components = fn_wrapper.roles["input"]
    arg_component = input_param_components[0].arg_component
    arg_props = input_param_components[0].arg_props
    expected_deps = flat_deps(arg_component, arg_props, "input")
    assert isinstance(arg_component, dcc.Slider)
    assert arg_props == "value"
    assert fn_wrapper._flat_input_deps[0] == expected_deps[0]

    # DatePickerRange
    input_param_components = fn_wrapper.roles["input"]
    arg_component = input_param_components[1].arg_component
    arg_props = input_param_components[1].arg_props
    expected_deps = flat_deps(arg_component, arg_props, "input")
    assert isinstance(arg_component, dcc.DatePickerRange)
    assert arg_props == ("start_date", "end_date")
    assert fn_wrapper._flat_input_deps[1:3] == expected_deps

    # Input Component as State
    input_param_components = fn_wrapper.roles["input"]
    arg_component = input_param_components[2].arg_component
    arg_props = input_param_components[2].arg_props
    expected_deps = flat_deps(arg_component, arg_props, "state")
    assert isinstance(arg_component, dcc.Input)
    assert arg_props == "value"
    assert fn_wrapper._flat_state_deps[0] == expected_deps[0]

    # Div as Output
    output_param_components = fn_wrapper.roles["output"]
    arg_component = output_param_components[0].arg_component
    arg_props = output_param_components[0].arg_props
    expected_deps = flat_deps(arg_component, arg_props, "output")
    assert isinstance(arg_component, dcc.Markdown)
    assert arg_props == "children"
    assert fn_wrapper._flat_output_deps[0] == expected_deps[0]


def test_pattern_dependencies(app, test_template):
    inputs = [(0, 10)]
    state = ["Initial input"]

    # Build mock function
    fn = mock_fn_with_return("Hello, world")
    fn_wrapper = app.callback(
        inputs=inputs, state=state, template=test_template
    )(fn)

    # call flat version (like dash would)
    assert fn_wrapper._flat_fn(
        1, "Some Text"
    ) == ["Hello, world"]

    # Check how mock function was called
    args, kwargs = fn.call_args
    assert args == (
        1, "Some Text"
    )
    assert not kwargs

    # Check dependencies
    # Slider
    input_param_components = fn_wrapper.roles["input"]
    arg_component = input_param_components[0].arg_component
    arg_props = input_param_components[0].arg_props
    expected_deps = flat_deps(arg_component, arg_props, "input")
    assert isinstance(arg_component, dcc.Slider)
    assert arg_props == "value"
    assert fn_wrapper._flat_input_deps[0] == expected_deps[0]

    # Input Component as State
    input_param_components = fn_wrapper.roles["input"]
    arg_component = input_param_components[1].arg_component
    arg_props = input_param_components[1].arg_props
    expected_deps = flat_deps(arg_component, arg_props, "state")
    assert isinstance(arg_component, dcc.Input)
    assert arg_props == "value"
    assert fn_wrapper._flat_state_deps[0] == expected_deps[0]

    # Div as Output
    output_param_components = fn_wrapper.roles["output"]
    arg_component = output_param_components[0].arg_component
    arg_props = output_param_components[0].arg_props
    expected_deps = flat_deps(arg_component, arg_props, "output")

    assert isinstance(arg_component, html.Div)
    assert arg_props == "children"
    assert fn_wrapper._flat_output_deps[0] == expected_deps[0]


def test_pattern_keyword_args(app, test_template):
    inputs = {
        "test_slider": (0, 10),
    }
    state = {"test_input": "Initial input"}
    output = {"test_output_markdown": dx.arg(dcc.Markdown(), props="children")}

    # Build mock function
    fn = mock_fn_with_return({"test_output_markdown": "Hello, world"})
    fn_wrapper = app.callback(
        output=output, inputs=inputs, state=state, template=test_template
    )(fn)

    # call flat version (like dash would)
    assert fn_wrapper._flat_fn(
        1, "Some Text"
    ) == ["Hello, world"]

    # Check how mock function was called
    args, kwargs = fn.call_args
    assert kwargs == {
        "test_slider": 1,
        "test_input": "Some Text",
    }
    assert not args

    # Check dependencies
    # Slider
    input_param_components = fn_wrapper.roles["input"]
    arg_component = input_param_components["test_slider"].arg_component
    arg_props = input_param_components["test_slider"].arg_props
    expected_deps = flat_deps(arg_component, arg_props, "input")
    assert isinstance(arg_component, dcc.Slider)
    assert arg_props == "value"
    assert fn_wrapper._flat_input_deps[0] == expected_deps[0]

    # Input Component as State
    arg_component = input_param_components["test_input"].arg_component
    arg_props = input_param_components["test_input"].arg_props
    expected_deps = flat_deps(arg_component, arg_props, "state")
    assert isinstance(arg_component, dcc.Input)
    assert arg_props == "value"
    assert fn_wrapper._flat_state_deps[0] == expected_deps[0]

    # Markdown Output
    output_param_components = fn_wrapper.roles["output"]
    arg_component = output_param_components["test_output_markdown"].arg_component
    arg_props = output_param_components["test_output_markdown"].arg_props
    expected_deps = flat_deps(arg_component, arg_props, "output")
    assert isinstance(arg_component, dcc.Markdown)
    assert arg_props == "children"
    assert fn_wrapper._flat_output_deps[0] == expected_deps[0]


def test_pattern_keyword_args_no_state(app, test_template):
    inputs = {
        "test_slider": (0, 10),
    }
    output = {"test_output_markdown": dx.arg(dcc.Markdown(), props="children")}

    # Build mock function
    fn = mock_fn_with_return({"test_output_markdown": "Hello, world"})
    fn_wrapper = app.callback(
        output=output, inputs=inputs, template=test_template
    )(fn)

    # call flat version (like dash would)
    assert fn_wrapper._flat_fn(1) == ["Hello, world"]

    # Check how mock function was called
    args, kwargs = fn.call_args
    assert kwargs == {
        "test_slider": 1,
    }
    assert not args

    # Check dependencies
    # Slider
    input_param_components = fn_wrapper.roles["input"]
    arg_component = input_param_components["test_slider"].arg_component
    arg_props = input_param_components["test_slider"].arg_props
    expected_deps = flat_deps(arg_component, arg_props, "input")
    assert isinstance(arg_component, dcc.Slider)
    assert arg_props == "value"
    assert fn_wrapper._flat_input_deps[0] == expected_deps[0]

    # Markdown Output
    output_param_components = fn_wrapper.roles["output"]
    arg_component = output_param_components["test_output_markdown"].arg_component
    arg_props = output_param_components["test_output_markdown"].arg_props
    expected_deps = flat_deps(arg_component, arg_props, "output")
    assert isinstance(arg_component, dcc.Markdown)
    assert arg_props == "children"
    assert fn_wrapper._flat_output_deps[0] == expected_deps[0]


def test_state_kwarg_only(app, test_template):
    state = {
        "test_input": dx.arg(dcc.Input()),
        "test_slider": dx.arg(dcc.Slider(), kind="input"),
    }
    output = {"test_output_markdown": dx.arg(dcc.Markdown(), props="children")}

    # Build mock function
    fn = mock_fn_with_return({"test_output_markdown": "Hello, world"})
    fn_wrapper = app.callback(
        output=output, state=state, template=test_template
    )(fn)

    # call flat version (like dash would)
    assert fn_wrapper._flat_fn(1, "input string") == ["Hello, world"]

    # Check how mock function was called
    args, kwargs = fn.call_args
    assert kwargs == {
        "test_slider": 1,
        "test_input": "input string",
    }
    assert not args

    # Check dependencies
    # Input
    input_param_components = fn_wrapper.roles["input"]
    arg_component = input_param_components["test_input"].arg_component
    arg_props = input_param_components["test_input"].arg_props
    expected_deps = flat_deps(arg_component, arg_props, "state")
    assert isinstance(arg_component, dcc.Input)
    assert arg_props == "value"
    assert fn_wrapper._flat_state_deps[0] == expected_deps[0]

    # Slider
    input_param_components = fn_wrapper.roles["input"]
    arg_component = input_param_components["test_slider"].arg_component
    arg_props = input_param_components["test_slider"].arg_props
    expected_deps = flat_deps(arg_component, arg_props, "input")
    assert isinstance(arg_component, dcc.Slider)
    assert arg_props == "value"
    assert fn_wrapper._flat_input_deps[0] == expected_deps[0]

    # Markdown Output
    output_param_components = fn_wrapper.roles["output"]
    arg_component = output_param_components["test_output_markdown"].arg_component
    arg_props = output_param_components["test_output_markdown"].arg_props
    expected_deps = flat_deps(arg_component, arg_props, "output")
    assert isinstance(arg_component, dcc.Markdown)
    assert arg_props == "children"
    assert fn_wrapper._flat_output_deps[0] == expected_deps[0]
