import dash
import dash_html_components as html
import dash_core_components as dcc
from dash.dependencies import Input, Output, ALL


class ST:
    @classmethod
    def callback_outputs(cls):
        return Output("output-div", "children"),

    @classmethod
    def callback_inputs(cls):
        return [Input({"type": ALL, "index": ALL}, "value")]

    def __init__(self, inputs_list):
        self.output = []
        self.inputs_list = inputs_list
        self.indexes = {}
        self.init_component_values()

    def init_component_values(self):
        indexes = [e["id"]["index"] for e in self.inputs_list[0]]
        types = [e["id"]["type"] for e in self.inputs_list[0]]
        values = [e["value"] for e in self.inputs_list[0]]
        sorted_tuples = sorted(zip(indexes, types, values), key=lambda e: e[0])

        component_values = {}
        for t in sorted_tuples:
            idx, typ, val = t
            component_values.setdefault(typ, []).append(val)

        self.component_values = component_values

    def _get_next_index_and_value(self, typ, default):
        component_ind = self.indexes.get(typ, 0)
        if component_ind < len(self.component_values.get(typ, [])):
            component_value = self.component_values[typ][component_ind]
        else:
            component_value = default

        # Increment index for component type
        self.indexes[typ] = component_ind + 1

        return component_ind, component_value

    def write(self, content):
        self.output.append(dcc.Markdown(content))

    def checkbox(self, label):
        component_ind, component_value = self._get_next_index_and_value("checkbox", [])
        self.output.append(dcc.Checklist(
            id={"type": "checkbox", "index": component_ind},
            options=[{"label": label, "value": label}],
            value=component_value
        ))
        return bool(component_value)

    def dropdown(self, options):
        if isinstance(options, list) and options and isinstance(options[0], str):
            options = [{"label": opt, "value": opt} for opt in options]

        component_ind, component_value = self._get_next_index_and_value("dropdown", options[0]["value"])
        self.output.append(dcc.Dropdown(
            id={"type": "dropdown", "index": component_ind},
            options=options,
            value=component_value,
        ))
        return component_value

    @property
    def layout(self):
        return [self.output]


def st_callback(app):
    app.layout = html.Div(id="output-div")
    def decorator(fn):
        @app.callback(
            ST.callback_outputs(),
            ST.callback_inputs(),
        )
        def dash_callback(_):
            inputs_list = dash.callback_context.inputs_list
            st = ST(inputs_list)
            fn(st)
            return st.layout
    return decorator


# Could this layout approach be used for interact?
#
def interact(app, ST):
    app.layout = html.Div(id="output-div")
    def decorator(fn):
        @app.callback(
            ST.callback_outputs(),
            ST.callback_inputs(),
        )
        def dash_callback(_):
            inputs_list = dash.callback_context.inputs_list
            st = ST(inputs_list)
            val = st.checkbox()
            st.add_component()
            st.add_dropdown()
            return st.layout
    return decorator
