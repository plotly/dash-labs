import dash_bootstrap_components as dbc
import dash_labs as dl
import dash

app = dash.Dash(__name__, plugins=[dl.plugins.FlexibleCallbacks()])
tpl = dl.templates.DbcCard(app, title="Simple App", columns=6)


@app.callback(
    tpl.new_button("Click Me", label="Button to click"),
    template=tpl,
)
def callback(n_clicks):
    return "Clicked {} times".format(n_clicks)


app.layout = dbc.Container(fluid=True, children=tpl.children)

if __name__ == "__main__":
    app.run_server(debug=True)
