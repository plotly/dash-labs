import dash
import dash_html_components as html


# Check outer div
def check_layout_body(layout_body, template):
    assert isinstance(layout_body, html.Div)
    assert layout_body.id == "all-div"
    assert len(layout_body.children) == 3

    # Check input div
    expected_input_components = [
        ac.container_component for ac in template.roles["input"].values()
    ]
    assert layout_body.children[0].id == "inputs-div"
    assert layout_body.children[0].children == expected_input_components

    # Check output div
    expected_output_components = [
        ac.container_component for ac in template.roles["output"].values()
    ]
    assert layout_body.children[1].id == "outputs-div"
    assert layout_body.children[1].children == expected_output_components

    # Check custom div
    expected_custom_components = [
        ac.container_component for ac in template.roles["custom"].values()
    ]
    assert layout_body.children[2].id == "customs-div"
    assert layout_body.children[2].children == expected_custom_components


def check_layout(template):
    app = dash.Dash()
    layout = template.layout(app, full=False)
    check_layout_body(layout, template)

    full_layout = template.layout(app, full=True)
    assert isinstance(full_layout, html.Div)
    assert full_layout.id == "app-div"
    assert len(full_layout.children) == 1
    check_layout_body(full_layout.children[0], template)
