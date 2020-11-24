import dash_express as dx
import dash_core_components as dcc

@dx.interact()
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
