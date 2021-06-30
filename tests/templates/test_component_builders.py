import datetime

import dash_html_components as html
import dash_core_components as dcc

from dash_labs import Input, State, Output
from ..fixtures import test_template


def test_dropdown_builder(test_template):
    options = [{"label": s.upper(), "value": s} for s in ["a", "b", "c"]]
    component_dep = test_template.new_dropdown(
        id="test-dropdown",
        options=options,
        value="b",
        opts=dict(disabled=True),
    )

    assert isinstance(component_dep, Input)
    assert component_dep.component_property == "value"
    component = component_dep.component_id

    assert isinstance(component, dcc.Dropdown)
    assert component.id == "test-dropdown"
    assert component.options == options
    assert component.value == "b"
    assert component.disabled is True


def test_slider_builder(test_template):
    min, max, step, val, id = 1, 10, 0.5, 5, "test-slider"
    component_dep = test_template.new_slider(
        min, max, id=id, value=val, opts=dict(disabled=True)
    )

    assert isinstance(component_dep, Input)
    assert component_dep.component_property == "value"
    component = component_dep.component_id

    assert isinstance(component, dcc.Slider)
    assert component.id == "test-slider"
    assert component.min == min
    assert component.max == max
    assert component.value == val
    assert component.disabled is True

    # Template enables persistent tooltips by default
    assert isinstance(component.tooltip, dict)

    # But can be overridden with tooltip argument, and can override kind to State
    component_dep = test_template.new_slider(
        min,
        max,
        id=id,
        value=val,
        kind=State,
        opts=dict(tooltip=None),
    )

    assert isinstance(component_dep, State)
    assert component_dep.component_property == "value"
    component = component_dep.component_id

    assert getattr(component, "tooltip", None) is None


def test_range_slider_builder(test_template):
    min, max, step, val, id = 1, 10, 0.5, [2, 5], "test-rangeslider"
    component_dep = test_template.new_range_slider(
        min, max, id=id, value=val, opts=dict(disabled=True)
    )

    assert isinstance(component_dep, Input)
    assert component_dep.component_property == "value"
    component = component_dep.component_id

    assert isinstance(component, dcc.RangeSlider)
    assert component.id == "test-rangeslider"
    assert component.min == min
    assert component.max == max
    assert component.value == val
    assert component.disabled is True

    # Template enables persistent tooltips by default
    assert isinstance(component.tooltip, dict)

    # But can be overridden with tooltip argument, and can override kind to State
    component_dep = test_template.new_range_slider(
        min,
        max,
        id=id,
        value=val,
        kind=State,
        opts=dict(tooltip=None),
    )

    assert isinstance(component_dep, State)
    assert component_dep.component_property == "value"
    component = component_dep.component_id

    assert getattr(component, "tooltip", None) is None


def test_input_builder(test_template):
    component_dep = test_template.new_textbox(
        "Starting", id="test-input", opts=dict(disabled=True)
    )

    assert isinstance(component_dep, Input)
    assert component_dep.component_property == "value"
    component = component_dep.component_id

    assert isinstance(component, dcc.Input)
    assert component.id == "test-input"
    assert component.value == "Starting"
    assert component.disabled is True


def test_checklist_builder(test_template):
    options = ["a", "b", "c"]
    expected_options = [{"label": s, "value": s} for s in options]

    component_dep = test_template.new_checklist(
        options,
        value=["b", "c"],
        id="test-checklist",
        opts=dict(className="checklist-class"),
    )

    assert isinstance(component_dep, Input)
    assert component_dep.component_property == "value"
    component = component_dep.component_id

    assert isinstance(component, dcc.Checklist)
    assert component.id == "test-checklist"
    assert component.options == expected_options
    assert component.value == ["b", "c"]
    assert component.className == "checklist-class"


def test_button_builder(test_template):
    component_dep = test_template.new_button(
        "Hello, world", id="test-button", opts=dict(disabled=True)
    )

    assert isinstance(component_dep, Input)
    assert component_dep.component_property == "n_clicks"
    component = component_dep.component_id

    assert isinstance(component, html.Button)
    assert component.id == "test-button"
    assert component.children == "Hello, world"
    assert component.disabled is True


def test_markdown_builder(test_template):
    component_dep = test_template.new_markdown(
        "Hello, world", id="test-markdown", opts=dict(dedent=False)
    )

    assert isinstance(component_dep, Output)
    assert component_dep.component_property == "children"
    component = component_dep.component_id

    assert isinstance(component, dcc.Markdown)
    assert component.id == "test-markdown"
    assert component.children == "Hello, world"
    assert component.dedent is False


def test_graph_builder(test_template):
    figure = dict(
        data=[dict(y=[1, 3, 2])], layout=dict(title=dict(text="Figure Title"))
    )
    config = dict(config_prop="config-val")
    component_dep = test_template.new_graph(
        figure=figure, id="test-graph", config=config
    )

    assert isinstance(component_dep, Output)
    assert component_dep.component_property == "figure"
    component = component_dep.component_id

    assert isinstance(component, dcc.Graph)
    assert component.figure == figure
    assert component.config == config


def test_date_picker_single_builder(test_template):
    today = datetime.date.today()
    component_dep = test_template.new_date_picker_single(
        today, id="test-datepicker", opts=dict(month_format="MM YY")
    )

    assert isinstance(component_dep, Input)
    assert component_dep.component_property == "date"
    component = component_dep.component_id

    assert isinstance(component, dcc.DatePickerSingle)
    assert component.date == today.isoformat()
    assert component.id == "test-datepicker"
    assert component.month_format == "MM YY"


def test_date_picker_range_builder(test_template):
    start_date = datetime.date(2000, 1, 1)
    end_date = datetime.date(200, 1, 15)

    component_dep = test_template.new_date_picker_range(
        start_date,
        end_date,
        id="test-daterangepicker",
        opts=dict(month_format="MM YY"),
    )

    assert isinstance(component_dep, Input)
    assert component_dep.component_property == ("start_date", "end_date")
    component = component_dep.component_id

    assert isinstance(component, dcc.DatePickerRange)
    assert component.start_date == start_date.isoformat()
    assert component.end_date == end_date.isoformat()
    assert component.id == "test-daterangepicker"
    assert component.month_format == "MM YY"
