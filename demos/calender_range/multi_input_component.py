import dash
import dash_express as dx
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
import dash_core_components as dcc

app = dash.Dash(__name__)
template = dx.templates.DbcSidebar(title="Dash Express App")
# template = dx.templates.DdkSidebar(title="Dash Express App")
# template = dx.templates.DccCard(title="Dash Express App")
# template = dx.templates.FlatDiv()


def callback_fn(input_val, date_range):
    print(input_val, date_range)
    return template.Graph(
        figure=go.Figure(layout_title_text=input_val + "-" + str(date_range))
    )


callback_components = dx.parameterize(
    app,
    callback_fn,
    input=dict(
        input_val="Initial Title",
        date_range=(dcc.DatePickerRange(), ["start_date", "end_date"])
    ),
    template=template,
    labels={
        "input_val": "Graph Title",
        "date_range": "Date: {value}",
    },
)

app.layout = callback_components.layout

if __name__ == "__main__":
    app.run_server(debug=True, port=9003)
