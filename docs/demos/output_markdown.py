import dash
import dash_core_components as dcc
import dash_express as dx

app = dash.Dash(__name__, plugins=[dx.Plugin()])

@app.callback(
    dx.Output(dcc.Markdown(), "children"),
    dx.Input(dcc.Textarea(value="## Heading\n"), label="Enter Markdown")
)
def markdown_preview(input_text):
    return input_text

app.layout = markdown_preview.layout(app)

if __name__ == "__main__":
    app.run_server(debug=True)
