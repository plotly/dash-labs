from dash.dependencies import Input, Output, State
import dash_html_components as html
import dash_core_components as dcc
import datetime

import dash_express as dx

from . import make_deps, mock_fn_with_return, assert_deps_eq
from ..fixtures import (
    app, test_template, tuple_grouping_size, dict_grouping_size, mixed_grouping_size
)


def test_arg_dependencies(app, test_template):
    inputs = [
        dx.arg(dcc.Slider(), label="Slider"),
        dx.arg(dcc.Dropdown(), label="Dropdown"),
    ]
    state = dx.arg(dcc.Input(), label="State Input")
    output = dx.arg(dcc.Markdown().props["children"], label="Markdown Output")

    # Build mock function
    fn = mock_fn_with_return("Hello, world")
    fn_wrapper = dx.callback(
        app, output, inputs, state, template=test_template
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


def test_component_dependencies(app, test_template):
    inputs = [dcc.Slider(), dcc.DatePickerRange().props[("start_date", "end_date")]]
    state = [dcc.Input()]
    output = dcc.Markdown().props["children"]

    # Build mock function
    fn = mock_fn_with_return("Hello, world")
    fn_wrapper = dx.callback(
        app, output, inputs, state, template=test_template
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
    assert_deps_eq(fn_wrapper._flat_output_deps, [output.output])

    # Check dependencies
    # Slider
    input_param_components = fn_wrapper.roles["input"]
    assert isinstance(input_param_components[0].value.component, dcc.Slider)
    assert input_param_components[0].value.props == "value"
    assert fn_wrapper._flat_input_deps[0] == input_param_components[0].value.input

    # DatePickerRange
    assert isinstance(input_param_components[1].value.component, dcc.DatePickerRange)
    assert input_param_components[1].value.props == ("start_date", "end_date")
    assert fn_wrapper._flat_input_deps[1:3] == input_param_components[1].value.flat_input

    # Input Component as State
    assert isinstance(input_param_components[2].value.component, dcc.Input)
    assert input_param_components[2].value.props == "value"
    assert fn_wrapper._flat_state_deps[0] == input_param_components[2].value.input

    # Div as Output
    output_param_components = fn_wrapper.roles["output"]
    assert isinstance(output_param_components[0].value.component, dcc.Markdown)
    assert output_param_components[0].value.props == "children"
    assert fn_wrapper._flat_output_deps[0] == output_param_components[0].value.input


def test_pattern_dependencies(app, test_template):
    inputs = [(0, 10)]
    state = ["Initial input"]

    # Build mock function
    fn = mock_fn_with_return("Hello, world")
    fn_wrapper = dx.callback(
        app, inputs=inputs, state=state, template=test_template
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
    assert isinstance(input_param_components[0].value.component, dcc.Slider)
    assert input_param_components[0].value.props == "value"
    assert fn_wrapper._flat_input_deps[0] == input_param_components[0].value.input

    # Input Component as State
    assert isinstance(input_param_components[1].value.component, dcc.Input)
    assert input_param_components[1].value.props == "value"
    assert fn_wrapper._flat_state_deps[0] == input_param_components[1].value.input

    # Div as Output
    output_param_components = fn_wrapper.roles["output"]
    assert isinstance(output_param_components[0].value.component, html.Div)
    assert output_param_components[0].value.props == "children"
    assert fn_wrapper._flat_output_deps[0] == output_param_components[0].value.input


def test_pattern_keyword_args(app, test_template):
    inputs = {
        "test_slider": (0, 10),
    }
    state = {"test_input": "Initial input"}
    output = {"test_output_markdown": dcc.Markdown().props["children"]}

    # Build mock function
    fn = mock_fn_with_return({"test_output_markdown": "Hello, world"})
    fn_wrapper = dx.callback(
        app, output=output, inputs=inputs, state=state, template=test_template
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
    assert isinstance(input_param_components["test_slider"].value.component, dcc.Slider)
    assert input_param_components["test_slider"].value.props == "value"
    assert fn_wrapper._flat_input_deps[0] == input_param_components["test_slider"].value.input

    # Input Component as State
    assert isinstance(input_param_components["test_input"].value.component, dcc.Input)
    assert input_param_components["test_input"].value.props == "value"
    assert fn_wrapper._flat_state_deps[0] == input_param_components["test_input"].value.input

    # Markdown Output
    output_param_components = fn_wrapper.roles["output"]
    assert isinstance(output_param_components["test_output_markdown"].value.component, dcc.Markdown)
    assert output_param_components["test_output_markdown"].value.props == "children"
    assert fn_wrapper._flat_output_deps[0] == output_param_components["test_output_markdown"].value.input


def test_pattern_keyword_args_no_state(app, test_template):
    inputs = {
        "test_slider": (0, 10),
    }
    output = {"test_output_markdown": dcc.Markdown().props["children"]}

    # Build mock function
    fn = mock_fn_with_return({"test_output_markdown": "Hello, world"})
    fn_wrapper = dx.callback(
        app, output=output, inputs=inputs, template=test_template
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
    assert isinstance(input_param_components["test_slider"].value.component, dcc.Slider)
    assert input_param_components["test_slider"].value.props == "value"
    assert fn_wrapper._flat_input_deps[0] == input_param_components["test_slider"].value.input

    # Markdown Output
    output_param_components = fn_wrapper.roles["output"]
    assert isinstance(output_param_components["test_output_markdown"].value.component, dcc.Markdown)
    assert output_param_components["test_output_markdown"].value.props == "children"
    assert fn_wrapper._flat_output_deps[0] == output_param_components["test_output_markdown"].value.input
