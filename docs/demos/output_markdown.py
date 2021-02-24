import dash
import dash_core_components as dcc
import dash_express as dx

app = dash.Dash(__name__, plugins=[dx.Plugin()])
tp = dx.templates.DbcSidebar("App Title")

@app.callback(
    output=tp.markdown(),
    inputs=tp.textarea("## Heading\n", opts=dict(style={"width": "100%", "height": 400})),
    template=tp
)
def markdown_preview(input_text):
    return input_text

app.layout = tp.layout(app)

if __name__ == "__main__":
    app.run_server(debug=True)
