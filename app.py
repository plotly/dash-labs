import dash
import dash_express

app = dash.Dash()

def greet(greeting, name, reps):
    return ("%s, %s! " % (greeting, name)) * reps

app.layout = dash_express.layout_from_callback(app, greet,
    greeting = ["Hello", "Hi", "Hey", "Yo"],
    name = "",
    reps = (1,10)
)

app.run_server(debug=True)
