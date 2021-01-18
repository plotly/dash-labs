import dash_express as dx
from dash.dependencies import Input, Output, State
import dash_core_components as dcc
import datetime
import dash_html_components as html

from . import mock_fn_with_return
from ..fixtures import app, test_template
from ..templates import check_layout_body


# Tests
def test_layout_from_pattern_keyword_args(app, test_template):
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

    # Check generated layout
    layout = fn_wrapper.layout(app, full=False)
    check_layout_body(layout, test_template)
