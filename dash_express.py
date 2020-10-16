import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output

def layout_from_callback(app, callback, **kwargs):
    input_components = []
    inputs = []
    for arg, pattern in kwargs.items():
        if isinstance(pattern, list):
            options = pattern
            inputs.append(Input(arg, "value"))
            input_components.append(dcc.Dropdown(
                id=arg,
                options = [{"label": opt, "value": opt} for opt in options],
                clearable = False,
                value=options[0]
            ))
        elif isinstance(pattern, tuple):
            minimum, maximum = pattern
            inputs.append(Input(arg, "value"))
            input_components.append(dcc.Slider(
                id=arg,
                min=minimum,
                max=maximum,
                value=int((maximum-minimum)/2)
            ))
        elif isinstance(pattern, str):
            inputs.append(Input(arg, "value"))
            input_components.append(dcc.Input(
                id=arg,
                value=pattern
            ))
        else:
            raise Exception("unknown pattern for " + arg)

    output_component = html.Div(id="output")
    output = Output("output", "children")

    app.callback(output, inputs)(callback)

    return html.Div(children=input_components + [output_component])
