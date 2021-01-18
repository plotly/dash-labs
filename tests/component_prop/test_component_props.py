from dash_express._component_props import ComponentProps
from dash_express.grouping import flatten_grouping, make_grouping_by_position

from ..fixtures import *

# Tests

# Test value
def test_string_value(component_str_prop):
    component, prop_str, val = component_str_prop
    component_prop = ComponentProps(component, prop_str)
    assert component_prop.value == val


def test_tuple_value(component_tuple_prop):
    component, prop_tuple, val = component_tuple_prop
    component_prop = ComponentProps(component, prop_tuple)
    assert component_prop.value == val


def test_dict_value(component_dict_prop):
    component, prop_dict, val = component_dict_prop
    component_prop = ComponentProps(component, prop_dict)
    assert component_prop.value == val


def test_mixed_value(component_mixed_prop):
    component, prop_grouping, val = component_mixed_prop
    component_prop = ComponentProps(component, prop_grouping)
    print(prop_grouping, val)
    assert component_prop.value == val

    # Test flat_values
    flat_expected = flatten_grouping(val)
    assert component_prop.flat_value == flat_expected


# Test dependency
def test_string_dependency(component_str_prop, dependency):
    component, prop_str, val = component_str_prop
    component_prop = ComponentProps(component, prop_str)
    dependency_attr = dependency.__name__.lower()
    expected = dependency(component.id, prop_str)
    result = getattr(component_prop, dependency_attr)
    assert result == expected
    assert isinstance(getattr(component_prop, dependency_attr), dependency)


def test_tuple_dependency(component_tuple_prop, dependency):
    component, prop_tuple, val = component_tuple_prop
    component_prop = ComponentProps(component, prop_tuple)
    dependency_attr = dependency.__name__.lower()
    expected = tuple(dependency(component.id, prop) for prop in prop_tuple)
    result = getattr(component_prop, dependency_attr)
    assert result == expected
    assert all(isinstance(el, dependency) for el in result)


def test_dict_dependency(component_dict_prop, dependency):
    component, prop_dict, val = component_dict_prop
    component_prop = ComponentProps(component, prop_dict)
    dependency_attr = dependency.__name__.lower()
    expected = {k: dependency(component.id, prop) for k, prop in prop_dict.items()}
    result = getattr(component_prop, dependency_attr)
    assert result == expected
    assert all(isinstance(el, dependency) for el in result.values())


def test_mixed_dependency(component_mixed_prop, dependency):
    component, props_grouping, vals_collection = component_mixed_prop
    component_prop = ComponentProps(component, props_grouping)
    dependency_attr = dependency.__name__.lower()
    result = getattr(component_prop, dependency_attr)
    flat_expected = [
        dependency(component.id, prop) for prop in flatten_grouping(props_grouping)
    ]
    expected = make_grouping_by_position(props_grouping, flat_expected)
    print(props_grouping, expected)
    assert result == expected

    # Check flat version
    flat_result = getattr(component_prop, "flat_" + dependency_attr)
    assert flat_result == flat_expected


# Test validation
def test_invalid_prop_str():
    component = html.Button()
    with pytest.raises(ValueError, match="bogus"):
        ComponentProps(component, "bogus")


def test_invalid_prop_tuple():
    component = html.Button()
    with pytest.raises(ValueError, match="bogus"):
        ComponentProps(component, ("n_clicks", "bogus"))


def test_invalid_prop_dict():
    component = html.Button()
    with pytest.raises(ValueError, match="bogus"):
        ComponentProps(component, {"n": "n_clicks", "b": "bogus"})


def test_invalid_prop_mixed():
    component = html.Button()
    with pytest.raises(ValueError, match="bogus"):
        ComponentProps(component, {"n": "n_clicks", "b": ("bogus", "title")})
