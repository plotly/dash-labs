from dash_express import ComponentProps
from ..fixtures import *


# Test component accessor and value
def test_string_value(component_str_prop):
    component, prop_str, val = component_str_prop
    component_prop = component.props[prop_str]
    assert isinstance(component_prop, ComponentProps)
    assert component_prop.value == val


def test_tuple_value(component_tuple_prop):
    component, prop_tuple, val = component_tuple_prop
    component_prop = component.props[prop_tuple]
    assert isinstance(component_prop, ComponentProps)
    assert component_prop.value == val


def test_dict_value(component_dict_prop):
    component, prop_dict, val = component_dict_prop
    component_prop = component.props[prop_dict]
    assert isinstance(component_prop, ComponentProps)
    assert component_prop.value == val


def test_mixed_value(component_mixed_prop):
    component, prop_grouping, val = component_mixed_prop
    component_prop = component.props[prop_grouping]
    assert isinstance(component_prop, ComponentProps)
    assert component_prop.value == val
