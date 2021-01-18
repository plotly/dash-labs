import dash_html_components as html
import pytest

from . import check_layout
from ..fixtures import test_template


def test_add_single_component_defaults(test_template):
    button = html.Button(id="button")
    pc = test_template.add_component(button)

    # Check inserted as input role
    assert len(test_template.roles["input"]) == 1
    assert len(test_template.roles["output"]) == 0
    assert test_template.roles["input"][0] is pc

    # Check ParameterComponent properties
    assert pc.value.component is button
    assert pc.value.id == "button"
    assert pc.value.props == ()

    # Check container
    assert pc.container.id == "container"
    assert pc.container.props == "children"
    assert pc.container.component.children is button

    # Check label
    assert pc.label is None

    # Check layout generation
    check_layout(test_template)


def test_add_component_options(test_template):
    button1 = html.Button(id="button1")

    # Add with containered false
    pc1 = test_template.add_component(
        button1, containered=False, value_property="n_clicks"
    )

    # Check inserted as input role
    assert len(test_template.roles["input"]) == 1
    assert len(test_template.roles["output"]) == 0
    assert test_template.roles["input"][0] is pc1

    # Check ParameterComponent properties
    assert pc1.value.component is button1
    assert pc1.value.id == "button1"
    assert pc1.value.props == "n_clicks"

    # Check container is just the vale and label is None
    assert pc1.container is pc1.value
    assert pc1.label is None

    # With label and name
    button2 = html.Button(id="button2")
    button3 = html.Button(id="button3")
    pc2 = test_template.add_component(
        button2, label="Button 2", value_property="n_clicks", name="button2_arg"
    )
    assert pc2.value.id == "button2"
    assert pc2.value.props == "n_clicks"
    assert pc2.label.value == "Button 2"
    assert pc2.label.id == "label"
    assert isinstance(pc2.label.component, html.Label)
    assert pc2.container.id == "container"
    assert pc2.container.props == "children"
    assert pc2.container.component.children == [
        pc2.label.component,
        pc2.value.component,
    ]

    pc3 = test_template.add_component(
        button3,
        label="Button 3",
        value_property="title",
    )
    assert pc3.value.id == "button3"
    assert pc3.value.props == "title"
    assert pc3.label.value == "Button 3"
    assert pc3.label.id == "label"
    assert isinstance(pc3.label.component, html.Label)
    assert pc3.container.id == "container"
    assert pc3.container.props == "children"
    assert pc3.container.component.children == [
        pc3.label.component,
        pc3.value.component,
    ]

    # Check inserted as input role
    assert len(test_template.roles["input"]) == 3
    assert len(test_template.roles["output"]) == 0
    assert test_template.roles["input"][0] is pc1
    assert test_template.roles["input"]["button2_arg"] is pc2
    assert test_template.roles["input"][2] is pc3

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

    pc1 = test_template.add_component(button1, role="input", name="button1")
    pc2 = test_template.add_component(button2, role="output")
    pc3 = test_template.add_component(button3, role="input")
    pc4 = test_template.add_component(button4, role="output", name="button4")

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

    pc1 = test_template.add_component(button1, role="input")
    pc2 = test_template.add_component(button2, role="output")
    pc3 = test_template.add_component(button3, role="custom")
    assert list(test_template.roles["input"].values()) == [pc1]
    assert list(test_template.roles["output"].values()) == [pc2]
    assert list(test_template.roles["custom"].values()) == [pc3]

    # Check validation when trying to add by unsupported custom role
    with pytest.raises(ValueError, match="bogus"):
        test_template.add_component(button3, role="bogus")

    # Check layout generation
    check_layout(test_template)


def test_add_by_index_position(test_template):
    button1 = html.Button(id="button1")
    button2 = html.Button(id="button2")
    button3 = html.Button(id="button3")

    pc1 = test_template.add_component(button1, name="arg1", role="output")
    pc3 = test_template.add_component(button3, role="output")
    pc2 = test_template.add_component(button2, name="arg2", role="output", before=1)
    assert list(test_template.roles["output"].values()) == [pc1, pc2, pc3]

    # Check layout generation
    check_layout(test_template)


def test_add_by_name_position(test_template):
    button1 = html.Button(id="button1")
    button2 = html.Button(id="button2")
    button3 = html.Button(id="button3")

    pc1 = test_template.add_component(button1, name="arg1", role="output")
    pc3 = test_template.add_component(button3, role="output")
    pc2 = test_template.add_component(button2, name="arg2", role="output", after="arg1")
    assert list(test_template.roles["output"].values()) == [pc1, pc2, pc3]

    # Check layout generation
    check_layout(test_template)
