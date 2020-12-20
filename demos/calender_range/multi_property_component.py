import dash
from dash.dependencies import Input

import dash_express as dx
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
import dash_core_components as dcc
import dash_html_components as html

app = dash.Dash(__name__)
template = dx.templates.DbcSidebar(title="Dash Express App")
# template = dx.templates.DdkSidebar(title="Dash Express App")
# template = dx.templates.DccCard(title="Dash Express App")
# template = dx.templates.FlatDiv()


def callback_fn(input_val, date_range):
    return template.Graph(
        figure=go.Figure(layout_title_text=input_val + "-" + str(date_range))
    )

daterange_id = dx.build_component_id("daterange", "daterange")
daterange = dcc.DatePickerRange(id=daterange_id)

layout = dx.parameterize(
    app,
    callback_fn,
    params=dict(
        input_val="Initial Title",
        # date_range=(dcc.DatePickerRange(), ["start_date", "end_date"])
        date_range=(Input(daterange_id, "start_date"), Input(daterange_id, "end_date")),
    ),
    template=template,
    labels={
        "input_val": "Graph Title",
        "date_range": "Date: {value}",
    },
    optional=["date_range"]
)

# Add daterange component outside of parameterize
layout.children.append(daterange)

app.layout = layout

if __name__ == "__main__":
    app.run_server(debug=True, port=9003)
