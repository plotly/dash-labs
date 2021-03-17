import dash
import dash_labs as dl

app = dash.Dash(__name__, plugins=[dl.Plugin()])
tpl = dl.templates.DbcSidebar("App Title", sidebar_columns=6)


@app.callback(
    output=tpl.markdown_output(),
    inputs=tpl.textarea_input(
        "## Heading\n", opts=dict(style={"width": "100%", "height": 400})
    ),
    template=tpl,
)
def markdown_preview(input_text):
    return input_text


app.layout = tpl.layout(app)

if __name__ == "__main__":
    app.run_server(debug=True)
