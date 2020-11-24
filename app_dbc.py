import dash_express as dx
import dash_core_components as dcc


@dx.interact(
    dx.layouts.dbc.DbcSidebarLayout(
        title="Dash Express App", sidebar_columns=4
    ),
    labels={
        "reps": "Repetitions: {value}",
        "name": "User Name",
        "greeting": "Preferred Greeting"
    },
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


if __name__ == "__main__":
    greet.run_server(debug=True)
