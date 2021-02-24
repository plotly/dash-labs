import dash_express as dx
import dash_html_components as html
import dash

app = dash.Dash(__name__, plugins=[dx.Plugin()])
tp = dx.templates.DbcCard(title="Simple App", columns=6)

div = html.Div()
button = html.Button(children="Click Me")

@app.callback(dx.Output(div, "children"), dx.Input(button, "n_clicks"))
def callback(n_clicks):
    return "Clicked {} times".format(n_clicks)

tp.add_component(button, label="Button to click", role="input")
tp.add_component(div, role="output")

app.layout = tp.layout(app)

if __name__ == "__main__":
    app.run_server(debug=True)
