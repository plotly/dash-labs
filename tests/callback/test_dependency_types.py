import pytest

from dash.dependencies import Input, Output, State
import dash_html_components as html
import dash_core_components as dcc
import datetime

import dash_labs as dl

from . import make_deps, mock_fn_with_return, assert_deps_eq
from ..fixtures import (
    app, test_template, tuple_grouping_size, dict_grouping_size, mixed_grouping_size
)
from ..helpers_for_testing import flat_deps


@pytest.mark.parametrize("input_form", [list, tuple])
def test_arg_dependencies(app, test_template, input_form):
    inputs = input_form([
        dl.Input(dcc.Slider(), label="Slider"),
        dl.Input(dcc.Dropdown(), label="Dropdown"),
    ])
    state = dl.State(dcc.Input(), label="State Input")
    output = dl.Output(dcc.Markdown(), "children", label="Markdown Output")

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
    inputs = dl.Input(dcc.DatePickerRange(), ("start_date", "end_date"))
    state = dl.State(dcc.Input())
    output = dl.Output(dcc.Markdown(), "children")

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
    inputs = dl.Input(html.Button(), "n_clicks")
    state = dl.State(dcc.Input())
    output = dl.Output(dcc.DatePickerRange(), ("start_date", "end_date"))

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


def test_state_kwarg_only(app, test_template):
    state = {
        "test_input": dl.State(dcc.Input()),
        "test_slider": dl.Input(dcc.Slider()),
    }
    output = {"test_output_markdown": dl.Output(dcc.Markdown(), "children")}

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
    input_param_components = test_template.roles["input"]
    arg_component = input_param_components["test_input"].arg_component
    arg_props = input_param_components["test_input"].arg_property
    expected_deps = flat_deps(arg_component, arg_props, "state")
    assert isinstance(arg_component, dcc.Input)
    assert arg_props == "value"
    assert fn_wrapper._flat_state_deps[0] == expected_deps[0]

    # Slider
    input_param_components = test_template.roles["input"]
    arg_component = input_param_components["test_slider"].arg_component
    arg_props = input_param_components["test_slider"].arg_property
    expected_deps = flat_deps(arg_component, arg_props, "input")
    assert isinstance(arg_component, dcc.Slider)
    assert arg_props == "value"
    assert fn_wrapper._flat_input_deps[0] == expected_deps[0]

    # Markdown Output
    output_param_components = test_template.roles["output"]
    arg_component = output_param_components["test_output_markdown"].arg_component
    arg_props = output_param_components["test_output_markdown"].arg_property
    expected_deps = flat_deps(arg_component, arg_props, "output")
    assert isinstance(arg_component, dcc.Markdown)
    assert arg_props == "children"
    assert fn_wrapper._flat_output_deps[0] == expected_deps[0]
