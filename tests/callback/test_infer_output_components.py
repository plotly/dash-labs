import dash_html_components as html
import dash_core_components as dcc
import dash_table
import plotly.graph_objects as go
import pandas as pd

import dash_express as dx

from . import make_deps, mock_fn_with_return, assert_deps_eq
from ..fixtures import app, test_template


def test_infer_output_components(app, test_template):
    inputs = [dx.Input(dcc.Slider(), label="Slider")]
    output = dx.Output(html.Div(), "children")

    # Build mock function
    button = html.Button(id="test-button")
    fn = mock_fn_with_return([
        go.Figure(data=[{"y": [1, 3, 2]}]),
        pd.DataFrame({"a": [1, 2, 3], "b": ["A", "BB", "CCC"]}),
        button
    ])
    fn_wrapper = app.callback(
        output=output, inputs=inputs, template=test_template
    )(fn)

    # call flat version (like dash would)
    result = fn_wrapper._flat_fn(1)[0]
    assert isinstance(result, list)
    assert len(result) == 3
    assert isinstance(result[0], dcc.Graph)
    assert isinstance(result[1], dash_table.DataTable)
    assert result[2] is button
