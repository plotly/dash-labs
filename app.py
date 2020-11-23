import dash
import dash_express as dx
import dash_html_components as html
import dash_bootstrap_components as dbc
import dash_design_kit as ddk
import dash_core_components as dcc

from dash_express.layouts.dbc import DbcRowLayout, DbcCardLayout, DbcSidebarLayout
from dash_express.layouts.ddk import DdkCardLayout, DdkRowLayout, DdkSidebarLayout
from dash_express.layouts.dcc import DccCardLayout

app = dash.Dash(__name__, external_stylesheets=[dbc.themes.DARKLY])


@dx.interact(
    # DccCardLayout(app, width="50%"),

    # DdkCardLayout(app, title="Dash Express App", width=40),
    # DdkRowLayout(app, title="Dash Express App", input_width=30),
    # DdkSidebarLayout(app, title="Dash Express App", sidebar_width="30%"),

    # DbcCardLayout(app, title="Dash Express App", columns=6),
    # DbcRowLayout(
    #     app, title="Dash Express App", input_cols=3, min_input_width="300px",
    # ),
    DbcSidebarLayout(app, title="Dash Express App", sidebar_columns=5),
    labels={
        "reps": "Repetitions: {value}",
        "name": "User Name",
        "greeting": "Prefered Greeting"
    },
)
def greet(
        greeting=["Hello", "Hi", "Hey", "Yo"],
        name="",
        reps=(1, 10)
):
    # return ("%s, %s! " % (greeting, name)) * reps
    # result = ddk.Graph(
    result=dcc.Graph(
        figure={
            "layout": {
                "title": {
                    "text": ("%s, %s! " % (greeting, name)) * reps
                }
            }
        }
    )
    return result


# app.layout = ddk.App(show_editor=True, children=greet.layout)

app.layout = html.Div(
    style={"padding": 30},
    children=greet.layout
)

if __name__ == "__main__":
    app.run_server(debug=True)
