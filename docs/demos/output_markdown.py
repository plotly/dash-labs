import dash
import dash_core_components as dcc
import dash_express as dx

app = dash.Dash(__name__)

@dx.callback(
    app,
    inputs={
        "input_text": dx.arg(
            dcc.Textarea(value="## Heading\n"), label="Enter Markdown"
        )
    },
    output=dcc.Markdown().props["children"],
)
def markdown_preview(input_text):
    return input_text


app.layout = markdown_preview.layout(app)

if __name__ == "__main__":
    app.run_server(debug=True)
