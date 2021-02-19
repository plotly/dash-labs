import dash_express as dx
from dash.dependencies import Input, Output, State
import dash_core_components as dcc

from . import mock_fn_with_return
from ..fixtures import app, test_template
from ..templates import check_layout_body


# Tests
def test_template_layout_generation(app, test_template):
    inputs = {
        "test_slider": dx.Input(dcc.Slider(min=0, max=10))
    }
    state = {"test_input": dx.State(dcc.Input(value="Initial input"))}
    output = {"test_output_markdown": dx.Output(dcc.Markdown(), "children")}

    # Build mock function
    fn = mock_fn_with_return({"test_output_markdown": "Hello, world"})
    fn_wrapper = dx.callback(
        app, output=output, inputs=inputs, state=state, template=test_template
    )(fn)

    # Check dependencies
    # Slider
    input_param_components = fn_wrapper.roles["input"]
    arg_component = input_param_components["test_slider"].arg_component
    arg_props = input_param_components["test_slider"].arg_props
    assert isinstance(arg_component, dcc.Slider)
    assert arg_props == "value"
    expect_input_deps = Input(arg_component.id, "value")
    assert fn_wrapper._flat_input_deps[0] == expect_input_deps

    # Input Component as State
    input_param_components = fn_wrapper.roles["input"]
    arg_component = input_param_components["test_input"].arg_component
    arg_props = input_param_components["test_input"].arg_props
    assert isinstance(arg_component, dcc.Input)
    assert arg_props == "value"
    expect_input_deps = Input(arg_component.id, "value")
    assert fn_wrapper._flat_state_deps[0] == expect_input_deps

    # Markdown Output
    output_param_components = fn_wrapper.roles["output"]
    arg_component = output_param_components["test_output_markdown"].arg_component
    arg_props = output_param_components["test_output_markdown"].arg_props
    assert isinstance(arg_component, dcc.Markdown)
    assert arg_props == "children"
    expect_output_deps = Input(arg_component.id, "children")
    assert fn_wrapper._flat_output_deps[0] == expect_output_deps

    # Check generated layout
    layout = fn_wrapper.layout(app, full=False)
    check_layout_body(layout, test_template)
