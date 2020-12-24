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


@dx.parameterize(
    inputs=dict(
        input_val="Initial Title",
        dates=dict(
            start_date=(dcc.DatePickerSingle(), "date"),
            end_date=(dcc.DatePickerSingle(), "date"),
        )
    ),
    output=[
        (template.Graph(), "figure"),
        (dcc.DatePickerRange(), ["start_date", "end_date"])
    ],
    template=template,
    labels={
        "input_val": "Graph Title",
        "date_range": "Date: {} to {}",
    },
)
def callback_components(input_val, dates):
    start_date, end_date = dates["start_date"], dates["end_date"]
    print(input_val, start_date, end_date)
    fig = go.Figure(layout_title_text=f"{input_val} - ({start_date}, {end_date})")
    return [fig, (start_date, end_date)]


app.layout = callback_components.layout(app)

if __name__ == "__main__":
    app.run_server(debug=True, port=9091)
