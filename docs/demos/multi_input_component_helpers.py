import dash
import dash_express as dx
import plotly.graph_objects as go
import dash_core_components as dcc

app = dash.Dash(__name__, plugins=[dx.Plugin()])
tp = dx.templates.DbcSidebar(title="App Title")

@app.callback(
    args=dict(
        figure_title=tp.input("Figure Title", label="Graph Title"),
        date_range=tp.date_picker_range("2010-03-12", label="Date")
    ),
)
def callback_components(figure_title, date_range):
    start_date, end_date = date_range
    if start_date:
        title = figure_title + ": " + str(start_date) + " to " + str(end_date)
    else:
        title = figure_title

    return go.Figure(
        layout_title_text=title
    )

app.layout = callback_components.layout(app)

if __name__ == "__main__":
    app.run_server(debug=True)
