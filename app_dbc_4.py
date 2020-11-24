import dash_express as dx
import dash_core_components as dcc
import dash
import dash_bootstrap_components as dbc
import dash_core_components as dcc

app = dash.Dash(__name__)

component_layout = dx.layouts.dbc.DbcSidebarLayout(
    app, title="My App Title", set_layout=False,
)

@dx.interact(
    component_layout,
    labels={
        "reps": "Repetitions: {value}",
        "name": "User Name",
        "greeting": "Preferred Greeting",
        "date": "Date of Greeting",
    },
)
def greet(
        greeting=dbc.Select(
            options=[{"label": v, "value": v} for v in ["Hello", "Hi", "Hey", "Yo"]],
            value="Hello",
        ),
        name=(dbc.Input(type="text", value=""), "value"),
        reps=dbc.Input(type="number", step=1, min=1, max=10, value=4),
        date=(dcc.DatePickerSingle(), "date"),
):
    result = dcc.Graph(
        figure={
            "layout": {
                "title": {
                    "text": ("%s, %s! " % (greeting, name)) * (reps or 0) + " on " + str(date)
                }
            }
        }
    )
    return result

app.layout = component_layout.layout()

if __name__ == "__main__":
    app.run_server(debug=True)
