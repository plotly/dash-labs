import datetime

import dash_html_components as html
import dash_core_components as dcc
import dash_table
from ..fixtures import test_template


def test_dropdown_builder(test_template):
    options = [{"label": s.upper(), "value": s} for s in ["a", "b", "c"]]
    component = test_template.Dropdown(
        id="test-dropdown",
        options=options,
        value="b",
        disabled=True,
    )

    assert isinstance(component, dcc.Dropdown)
    assert component.id == "test-dropdown"
    assert component.options == options
    assert component.value == "b"
    assert component.disabled is True


def test_slider_builder(test_template):
    min, max, step, val, id = 1, 10, 0.5, 5, "test-slider"
    component = test_template.Slider(min=min, max=max, id=id, value=val, disabled=True)

    assert isinstance(component, dcc.Slider)
    assert component.id == "test-slider"
    assert component.min == min
    assert component.max == max
    assert component.value == val
    assert component.disabled is True

    # Template enables persistent tooltips by default
    assert isinstance(component.tooltip, dict)

    # But can be overridden with tooltip argument
    component = test_template.Slider(min=min, max=max, id=id, value=val, tooltip=None)
    assert getattr(component, "tooltip", None) is None


def test_input_builder(test_template):
    component = test_template.Input(id="test-input", value="Starting", disabled=True)
    assert isinstance(component, dcc.Input)
    assert component.id == "test-input"
    assert component.value == "Starting"
    assert component.disabled is True


def test_checklist_builder(test_template):
    options = [{"label": s.upper(), "value": s} for s in ["a", "b", "c"]]
    component = test_template.Checklist(
        id="test-checklist",
        options=options,
        value=["b", "c"],
        className="checklist-class",
    )

    assert isinstance(component, dcc.Checklist)
    assert component.id == "test-checklist"
    assert component.options == options
    assert component.value == ["b", "c"]
    assert component.className == "checklist-class"


def test_button_builder(test_template):
    component = test_template.Button("Hello, world", id="test-button", disabled=True)

    assert isinstance(component, html.Button)
    assert component.id == "test-button"
    assert component.children == "Hello, world"
    assert component.disabled is True


def test_markdown_builder(test_template):
    component = test_template.Markdown("Hello, world", id="test-markdown", dedent=False)

    assert isinstance(component, dcc.Markdown)
    assert component.id == "test-markdown"
    assert component.children == "Hello, world"
    assert component.dedent is False


def test_graph_builder(test_template):
    figure = dict(
        data=[dict(y=[1, 3, 2])], layout=dict(title=dict(text="Figure Title"))
    )
    config = dict(config_prop="config-val")
    component = test_template.Graph(figure=figure, id="test-graph", config=config)

    assert isinstance(component, dcc.Graph)
    assert component.figure == figure
    assert component.config == config


def test_datatable_builder(test_template):
    import plotly.express as px

    df = px.data.tips()
    data = df.to_dict("records")
    columns = df.columns.tolist()

    component = test_template.DataTable(
        data, columns=columns, id="test-datatable", page_size=25
    )
    assert isinstance(component, dash_table.DataTable)
    assert component.data == data
    assert component.columns == columns
    assert component.page_size == 25


def test_date_picker_single_builder(test_template):
    today = datetime.date.today()
    component = test_template.DatePickerSingle(
        date=today, id="test-datepicker", month_format="MM YY"
    )
    assert isinstance(component, dcc.DatePickerSingle)
    assert component.date == today.isoformat()
    assert component.id == "test-datepicker"
    assert component.month_format == "MM YY"


def test_date_picker_range_builder(test_template):
    start_date = datetime.date(2000, 1, 1)
    end_date = datetime.date(200, 1, 15)
    component = test_template.DatePickerRange(
        start_date=start_date,
        end_date=end_date,
        id="test-daterangepicker",
        month_format="MM YY",
    )

    assert isinstance(component, dcc.DatePickerRange)
    assert component.start_date == start_date.isoformat()
    assert component.end_date == end_date.isoformat()
    assert component.id == "test-daterangepicker"
    assert component.month_format == "MM YY"
