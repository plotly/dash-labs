import dash
import dash_express as dx
import plotly.graph_objects as go
import dash_core_components as dcc

app = dash.Dash(__name__)


@dx.parameterize(
    app,
    inputs=dict(
        figure_title="Initial Title",
        date_range=(dcc.DatePickerRange(), ["start_date", "end_date"])
    ),
    labels={
        "figure_title": "Graph Title",
        "date_range": "Date: {} to {}",
    },
)
def callback_components(figure_title, date_range):
    return dcc.Graph(
        figure=go.Figure(layout_title_text=figure_title + "-" + str(date_range))
    )

app.layout = callback_components.layout(app)

if __name__ == "__main__":
    app.run_server(debug=True, port=9003)
