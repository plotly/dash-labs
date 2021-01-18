import datetime

import dash_html_components as html
import dash_core_components as dcc
import dash_table
import pytest

from dash_express import ComponentProps
from ..fixtures import test_template


# Helpers
def from_pattern_check_id(template, pattern):
    component_props = template.infer_input_component_props_from_pattern(pattern, id="custom-id")
    assert isinstance(component_props, ComponentProps)
    component = component_props.component
    assert component.id == "custom-id"
    return component_props


# Tests
def test_component_props_passed_through(test_template):
    pattern = ComponentProps(dcc.Slider(min=0, max=10, id="slider-pattern"), "value")
    component_props = test_template.infer_input_component_props_from_pattern(
        pattern=pattern, id="unused-id"
    )
    assert component_props is pattern

    # Non "value" prop
    pattern = dcc.DatePickerSingle(date=datetime.date.today()).props["date"]
    component_props = test_template.infer_input_component_props_from_pattern(
        pattern=pattern, id="unused-id"
    )
    assert component_props is pattern


def test_component_uses_value_as_default_prop(test_template):
    pattern = dcc.Slider(min=0, max=10, id="slider-pattern")
    component_props = test_template.infer_input_component_props_from_pattern(
        pattern=pattern, id="unused-id"
    )
    assert isinstance(component_props, ComponentProps)
    assert component_props.component is pattern
    assert component_props.id == "slider-pattern"
    assert component_props.props == "value"


def test_component_raise_if_value_unavailable(test_template):
    pattern = dcc.DatePickerSingle()
    with pytest.raises(ValueError, match="value"):
        test_template.infer_input_component_props_from_pattern(pattern=pattern)


def test_list_to_dropdown(test_template):
    pattern = ["A", "BB", "CCC"]
    component_props = from_pattern_check_id(test_template, pattern)
    component = component_props.component

    assert isinstance(component, dcc.Dropdown)
    assert component_props.props == "value"
    assert component_props.value == "A"
    assert component.options == [{"label": v, "value": v} for v in pattern]
    assert component.value == "A"


def test_number_tuple_to_slider(test_template):
    pattern = (-10, 100)
    component_props = from_pattern_check_id(test_template, pattern)
    component = component_props.component

    assert isinstance(component, dcc.Slider)
    assert component_props.props == "value"
    assert component_props.value == -10
    assert component.value == -10
    assert component.min == -10
    assert component.max == 100
    assert not hasattr(component, "step")


def test_number_tuple_to_slider_with_step(test_template):
    pattern = (-10, 100, 10)
    component_props = from_pattern_check_id(test_template, pattern)
    component = component_props.component

    assert isinstance(component, dcc.Slider)
    assert component_props.props == "value"
    assert component_props.value == -10
    assert component.value == -10
    assert component.min == -10
    assert component.max == 100
    assert component.step == 10


def test_string_to_input(test_template):
    pattern = "Hello, World"
    component_props = from_pattern_check_id(test_template, pattern)
    component = component_props.component

    assert isinstance(component, dcc.Input)
    assert component_props.props == "value"
    assert component_props.value == pattern
    assert component.value == pattern


def test_bool_to_checkbox(test_template):
    pattern = True
    component_props = from_pattern_check_id(test_template, pattern)
    component = component_props.component

    assert isinstance(component, dcc.Checklist)
    assert component_props.props == "value"
    assert component_props.value == ["checked"]
    assert component.value == ["checked"]
    assert component.options == [{"label": "", "value": "checked"}]

