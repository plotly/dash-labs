import dash
import dash_express as dx
import dash_html_components as html
import dash_bootstrap_components as dbc

app = dash.Dash(__name__)
import dash_design_kit as ddk


@dx.interact(
    app,
    labels={
        "reps": "Repetitions: {value}",
        "name": "User Name",
        "greeting": "Prefered Greeting"
    },
    title="Dash Express App",

    template="dcc_card",
    width="50%",

    # template="ddk_card",
    # width=50,

    # template="dbc_card",
    # width="50%",
)
def greet(
        greeting=["Hello", "Hi", "Hey", "Yo"],
        name="",
        reps=(1, 10)
):
    return ("%s, %s! " % (greeting, name)) * reps
    # result = ddk.Graph(
    #     figure={
    #         "layout": {
    #             "title": {
    #                 "text": ("%s, %s! " % (greeting, name)) * reps
    #             }
    #         }
    #     }
    # )
    # return result


# app.layout = ddk.App(show_editor=True, children=[
#     greet.layout
# ])

app.layout = html.Div(
    style={"padding": 30},
    children=greet.layout
)

if __name__ == "__main__":
    app.run_server(debug=True)
