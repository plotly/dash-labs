import dash_html_components as html
from dash_labs.util import add_css_class


def test_add_css_class_when_undefined():
    div = html.Div()
    assert not hasattr(div, "className")

    # Add a class
    add_css_class(div, "test-class1")

    # Check class string
    assert div.className == "test-class1"

    # Add it again and make sure nothing changed
    add_css_class(div, "test-class1")
    assert div.className == "test-class1"


def test_add_css_class_when_defined_as_none():
    div = html.Div(className=None)
    assert div.className is None

    # Add a class
    add_css_class(div, "test-class1")

    # Check class string
    assert div.className == "test-class1"


def test_add_css_class_when_one_already_defined():
    # Initialize className string with extraneous space
    div = html.Div(className=" test-class1")

    # Add className string with extraneous space
    add_css_class(div, "test-class2 ")

    # Check classes string
    assert div.className == "test-class1 test-class2"

    # Add it again and make sure nothing changed
    add_css_class(div, "test-class2")
    assert div.className == "test-class1 test-class2"


def test_add_css_class_when_multiple_already_defined():
    # Initialize className string with two classes and extraneous spaces
    div = html.Div(className="  test-class1  test-class2  ")

    # Add className string with extraneous space
    add_css_class(div, " test-class3 ")

    # Check classes string
    assert div.className == "test-class1 test-class2 test-class3"

    # Add it again and make sure nothing changed
    add_css_class(div, "test-class3")
    assert div.className == "test-class1 test-class2 test-class3"


def test_add_multi_class_string():
    # Initialize className string with two classes and extraneous spaces
    div = html.Div(className="  test-class1  test-class2  ")

    # Add className string with extraneous space
    add_css_class(div, " test-class3  test-class4")

    # Check classes string
    assert div.className == "test-class1 test-class2 test-class3 test-class4"

    # Add it again and make sure nothing changed
    add_css_class(div, " test-class3  test-class4")
    assert div.className == "test-class1 test-class2 test-class3 test-class4"


def test_add_multi_class_list():
    # Initialize className string with two classes and extraneous spaces
    div = html.Div(className="  test-class1  test-class2  ")

    # Add className string with extraneous space
    add_css_class(div, ["test-class3 ", "  test-class4 "])

    # Check classes string
    assert div.className == "test-class1 test-class2 test-class3 test-class4"

    # Add it again and make sure nothing changed
    add_css_class(div, ["test-class3", "test-class4"])
    assert div.className == "test-class1 test-class2 test-class3 test-class4"


def test_add_none():
    div = html.Div(className="test-class1")
    add_css_class(div, None)
    assert div.className == "test-class1"


def test_add_empty_string():
    div = html.Div(className="test-class1 test-class2")
    add_css_class(div, "")
    assert div.className == "test-class1 test-class2"


def test_add_empty_list():
    div = html.Div(className="test-class1 test-class2")
    add_css_class(div, [])
    assert div.className == "test-class1 test-class2"
