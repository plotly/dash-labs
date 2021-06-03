import dash
import dash_labs as dl
import dash_bootstrap_components as dbc

app = dash.Dash(__name__, plugins=[dl.plugins.FlexibleCallbacks()])
tpl = dl.templates.DbcSidebar(app, "App Title", sidebar_columns=6)


@app.callback(
    output=tpl.new_markdown(),
    args=tpl.new_textarea(
        "## Heading\n", opts=dict(style={"width": "100%", "height": 400})
    ),
    template=tpl,
)
def markdown_preview(input_text):
    return input_text


app.layout = dbc.Container(fluid=True, children=tpl.children)

if __name__ == "__main__":
    app.run_server(debug=True)
