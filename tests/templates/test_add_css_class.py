import dash_html_components as html
from ..fixtures import test_template


def test_css_class_not_added_to_all_components(test_template):
    div = html.Div()
    test_template.add_component(div)
    assert not hasattr(div, "className")


def test_css_class_added_to_specific_components(test_template):
    # TestTemplate adds the test-button-css-class class to html.Button components
    button = html.Button()
    test_template.add_component(button)
    assert button.className == "test-button-css-class"


def test_css_class_appended_to_existing_classes(test_template):
    # TestTemplate adds the test-button-css-class class to html.Button components
    button = html.Button(className="user-defined-class")
    test_template.add_component(button)
    assert button.className == "user-defined-class test-button-css-class"
