import dash_html_components as html
import pytest

from . import check_layout
from ..fixtures import test_template


def test_add_single_component_defaults(test_template):
    button = html.Button(id="button")
    arg_comps = test_template.add_component(button, "input")

    # Check inserted as input role
    assert len(test_template.roles["input"]) == 1
    assert len(test_template.roles["output"]) == 0
    assert test_template.roles["input"][0] is arg_comps

    # Check ParameterComponent properties
    assert arg_comps.arg_component is button
    assert arg_comps.arg_component.id == "button"
    assert arg_comps.arg_property is None

    # Check container
    assert arg_comps.container_component.id == "container"
    assert arg_comps.container_property == "children"
    assert arg_comps.container_component.children is button

    # Check label
    assert arg_comps.label_component is None
    assert arg_comps.label_property is None

    # Check layout generation
    check_layout(test_template)


def test_add_component_options(test_template):
    button1 = html.Button(id="button1")

    arg_comps1 = test_template.add_component(
        button1,
        "input",
        component_property="n_clicks",
    )

    # Check inserted as input role
    assert len(test_template.roles["input"]) == 1
    assert len(test_template.roles["output"]) == 0
    assert test_template.roles["input"][0] is arg_comps1

    # Check ParameterComponent properties
    assert arg_comps1.arg_component is button1
    assert arg_comps1.arg_component.id == "button1"
    assert arg_comps1.arg_property == "n_clicks"

    # Check that container and label are None
    assert isinstance(arg_comps1.container_component, html.Div)
    assert arg_comps1.container_property is "children"
    assert arg_comps1.label_component is None
    assert arg_comps1.label_property is None

    # With label and name
    button2 = html.Button(id="button2")
    button3 = html.Button(id="button3")
    arg_comps2 = test_template.add_component(
        button2,
        "input",
        component_property="n_clicks",
        label="Button 2",
        name="button2_arg",
        label_id="label",
    )
    assert arg_comps2.arg_component.id == "button2"
    assert arg_comps2.arg_property == "n_clicks"
    assert arg_comps2.label_component.children == "Button 2"
    assert arg_comps2.label_component.id == "label"
    assert isinstance(arg_comps2.label_component, html.Label)

    assert arg_comps2.container_component.id == "container"
    assert arg_comps2.container_property == "children"
    assert arg_comps2.container_component.children == [
        arg_comps2.label_component,
        arg_comps2.arg_component,
    ]

    arg_comps3 = test_template.add_component(
        button3, "input", component_property="title", label="Button 3", label_id="label"
    )
    assert arg_comps3.arg_component.id == "button3"
    assert arg_comps3.arg_property == "title"
    assert arg_comps3.label_component.children == "Button 3"
    assert arg_comps3.label_component.id == "label"
    assert isinstance(arg_comps3.label_component, html.Label)
    assert arg_comps3.container_component.id == "container"
    assert arg_comps3.container_property == "children"
    assert arg_comps3.container_component.children == [
        arg_comps3.label_component,
        arg_comps3.arg_component,
    ]

    # Check inserted as input role
    assert len(test_template.roles["input"]) == 3
    assert len(test_template.roles["output"]) == 0
    assert test_template.roles["input"][0] is arg_comps1
    assert test_template.roles["input"]["button2_arg"] is arg_comps2
    assert test_template.roles["input"][2] is arg_comps3

    # Check order of values
    assert list(test_template.roles["input"]) == [0, "button2_arg", 2]

    # Check layout generation
    check_layout(test_template)


def test_add_components_by_role(test_template):
    # With label and name
    button1 = html.Button(id="button1")
    button2 = html.Button(id="button2")
    button3 = html.Button(id="button3")
    button4 = html.Button(id="button4")

    pc1 = test_template.add_component(button1, "input", name="button1")
    pc2 = test_template.add_component(button2, "output")
    pc3 = test_template.add_component(button3, "input")
    pc4 = test_template.add_component(button4, "output", name="button4")

    # Check input / output keys
    assert list(test_template.roles["input"]) == ["button1", 1]
    assert list(test_template.roles["output"]) == [0, "button4"]

    # Check values
    assert list(test_template.roles["input"].values()) == [pc1, pc3]
    assert list(test_template.roles["output"].values()) == [pc2, pc4]

    # Check layout generation
    check_layout(test_template)


def test_add_by_custom_role(test_template):
    # With label and name
    button1 = html.Button(id="button1")
    button2 = html.Button(id="button2")
    button3 = html.Button(id="button3")

    pc1 = test_template.add_component(button1, "input")
    pc2 = test_template.add_component(button2, "output")
    pc3 = test_template.add_component(button3, "custom")
    assert list(test_template.roles["input"].values()) == [pc1]
    assert list(test_template.roles["output"].values()) == [pc2]
    assert list(test_template.roles["custom"].values()) == [pc3]

    # Check validation when trying to add by unsupported custom role
    with pytest.raises(ValueError, match="bogus"):
        test_template.add_component(button3, "bogus")

    # Check layout generation
    check_layout(test_template)


def test_add_by_index_position(test_template):
    button1 = html.Button(id="button1")
    button2 = html.Button(id="button2")
    button3 = html.Button(id="button3")

    pc1 = test_template.add_component(button1, "output", name="arg1")
    pc3 = test_template.add_component(button3, "output")
    pc2 = test_template.add_component(button2, "output", name="arg2", before=1)
    assert list(test_template.roles["output"].values()) == [pc1, pc2, pc3]

    # Check layout generation
    check_layout(test_template)


def test_add_by_name_position(test_template):
    button1 = html.Button(id="button1")
    button2 = html.Button(id="button2")
    button3 = html.Button(id="button3")

    pc1 = test_template.add_component(button1, "output", name="arg1")
    pc3 = test_template.add_component(button3, "output")
    pc2 = test_template.add_component(button2, "output", name="arg2", after="arg1")
    assert list(test_template.roles["output"].values()) == [pc1, pc2, pc3]

    # Check layout generation
    check_layout(test_template)
