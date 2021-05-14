import dash_labs as dl
import dash_html_components as html
import dash_bootstrap_components as dbc
import dash


app = dash.Dash(__name__, plugins=[dl.plugins.FlexibleCallbacks()])
tpl = dl.templates.DbcCard(app, title="Simple App", columns=4)

div = html.Div()
button = html.Button(children="Click Me")


@app.callback(dl.Output(div, "children"), dl.Input(button, "n_clicks"))
def callback(n_clicks):
    return "Clicked {} times".format(n_clicks)


tpl.add_component(button, label="Button to click", role="input")
tpl.add_component(div, role="output")

app.layout = dbc.Container(fluid=True, children=tpl.children)

if __name__ == "__main__":
    app.run_server(debug=True)
