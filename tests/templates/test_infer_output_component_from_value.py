import pandas as pd

import dash_html_components as html
import dash_core_components as dcc
import dash_table
import plotly.graph_objects as go

from ..fixtures import test_template


# Tests
def test_components_passed_through(test_template):
    button = html.Button(id="test-button")
    result = test_template.infer_output_component_from_value(button)
    assert result is button


def test_figure_inferred_to_graph(test_template):
    fig = go.Figure(data=[{"y": [1, 3, 2]}])
    result = test_template.infer_output_component_from_value(fig)

    assert isinstance(result, dcc.Graph)
    assert result.figure is fig
    assert "uid" in result.id


def test_dataframe_inferred_to_datatable(test_template):
    df = pd.DataFrame({"a": [1, 2, 3], "b": ["A", "BB", "CCC"]})
    result = test_template.infer_output_component_from_value(df)

    assert isinstance(result, dash_table.DataTable)
    assert result.columns == [{"id": c, "name": c} for c in df.columns]
    assert result.data == df.to_dict("records")


def test_inferrence_over_list(test_template):
    button = html.Button(id="test-button")
    fig = go.Figure(data=[{"y": [1, 3, 2]}])
    df = pd.DataFrame({"a": [1, 2, 3], "b": ["A", "BB", "CCC"]})
    result = test_template.infer_output_component_from_value([
        button,
        fig,
        df,
    ])

    assert isinstance(result, list) and len(result) == 3
    assert result[0] is button
    assert isinstance(result[1], dcc.Graph)
    assert result[1].figure is fig
    assert isinstance(result[2], dash_table.DataTable)
    assert result[2].columns == [{"id": c, "name": c} for c in df.columns]
    assert result[2].data == df.to_dict("records")
