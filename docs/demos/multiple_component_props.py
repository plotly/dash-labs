import dash
import dash_labs as dl
import plotly.graph_objects as go
import dash_core_components as dcc

app = dash.Dash(__name__, plugins=[dl.plugins.FlexibleCallbacks()])
tpl = dl.templates.FlatDiv(app)


@app.callback(
    args=dict(
        figure_title=tpl.textbox_input("Figure Title", label="Graph Title"),
        # figure_title=dl.Input(dcc.Input(value="Figure Title"), label="Graph Title"),
        date_range=tpl.date_picker_range_input(label="Date"),
        # date_range=dl.Input(dcc.DatePickerRange(), ("start_date", "end_date"), label="Date")
    ),
    template=tpl,
)
def callback_components(figure_title, date_range):
    start_date, end_date = date_range
    if start_date:
        title = figure_title + ": " + str(start_date) + " to " + str(end_date)
    else:
        title = figure_title

    return dcc.Graph(figure=go.Figure(layout_title_text=title))


app.layout = tpl.children

if __name__ == "__main__":
    app.run_server(debug=True)
