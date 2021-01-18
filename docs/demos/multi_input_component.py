import dash
import dash_express as dx
import plotly.graph_objects as go
import dash_core_components as dcc

app = dash.Dash(__name__)


@dx.callback(
    app,
    inputs=dict(
        figure_title=dx.arg("Initial Title", label="Graph Title"),
        date_range=dx.arg(
            dcc.DatePickerRange().props[("start_date", "end_date")], label="Date"
        )
    ),
)
def callback_components(figure_title, date_range):
    start_date, end_date = date_range
    if start_date:
        title = figure_title + ": " + str(start_date) + " to " + str(end_date)
    else:
        title = figure_title

    return dcc.Graph(
        figure=go.Figure(
            layout_title_text=title
        )
    )


app.layout = callback_components.layout(app)

if __name__ == "__main__":
    app.run_server(debug=True)
