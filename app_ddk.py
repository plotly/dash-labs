import dash_express as dx
import dash_design_kit as ddk
from dash_express.layouts.ddk import DdkSidebarLayout


@dx.interact(
    DdkSidebarLayout(
        title="Dash Express App", sidebar_width="30%", show_editor=True
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
    result = ddk.Graph(
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
