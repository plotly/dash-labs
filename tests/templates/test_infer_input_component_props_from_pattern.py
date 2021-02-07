import dash_core_components as dcc
from ..fixtures import test_template


# Tests
def test_list_to_dropdown(test_template):
    pattern = ["A", "BB", "CCC"]
    component, props = test_template.infer_component_and_props_from_pattern(pattern)

    assert isinstance(component, dcc.Dropdown)
    assert props == "value"
    assert component.value == "A"
    assert component.options == [{"label": v, "value": v} for v in pattern]


def test_number_tuple_to_slider(test_template):
    pattern = (-10, 100)
    component, props = test_template.infer_component_and_props_from_pattern(pattern)

    assert isinstance(component, dcc.Slider)
    assert props == "value"
    assert component.value == -10
    assert component.min == -10
    assert component.max == 100
    assert not hasattr(component, "step")


def test_number_tuple_to_slider_with_step(test_template):
    pattern = (-10, 100, 10)
    component, props = test_template.infer_component_and_props_from_pattern(pattern)

    assert isinstance(component, dcc.Slider)
    assert props == "value"
    assert component.value == -10
    assert component.min == -10
    assert component.max == 100
    assert component.step == 10


def test_string_to_input(test_template):
    pattern = "Hello, World"
    component, props = test_template.infer_component_and_props_from_pattern(pattern)

    assert isinstance(component, dcc.Input)
    assert props == "value"
    assert component.value == pattern


def test_bool_to_checkbox(test_template):
    pattern = True
    component, props = test_template.infer_component_and_props_from_pattern(pattern)

    assert isinstance(component, dcc.Checklist)
    assert props == "value"
    assert component.value == ["checked"]
    assert component.options == [{"label": "", "value": "checked"}]

