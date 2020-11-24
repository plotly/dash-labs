import dash_express as dx
import dash_core_components as dcc
import dash

app = dash.Dash(__name__)

@dx.interact(
    dx.layouts.dbc.DbcSidebarLayout(
        app, title="My App Title", set_layout=False,
    )
)
def greet(
        greeting=["Hello", "Hi", "Hey", "Yo"],
        name="",
        reps=(1, 10)
):
    result = dcc.Graph(
        figure={
            "layout": {
                "title": {
                    "text": ("%s, %s! " % (greeting, name)) * reps
                }
            }
        }
    )
    return result

app.layout = greet.layout()

if __name__ == "__main__":
    app.run_server(debug=True)
