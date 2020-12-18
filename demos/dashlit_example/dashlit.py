import dash
import dash_html_components as html
import dash_core_components as dcc
from dash.dependencies import Input, Output, ALL

from templates.div import FlatDiv
from templates.util import build_component_pattern


class ST:
    def __init__(self, inputs_list, template_instance):
        self.output = []
        self.inputs_list = inputs_list
        self.template_instance = template_instance
        self.indexes = {}
        self.init_component_values()

    def init_component_values(self):
        indexes = [e["id"]["name"] for e in self.inputs_list[0]]
        types = [e["id"]["kind"] for e in self.inputs_list[0]]
        values = [e["value"] for e in self.inputs_list[0]]

        sorted_tuples = sorted(zip(indexes, types, values), key=lambda e: e[0])

        component_values = {}
        for t in sorted_tuples:
            idx, typ, val = t
            component_values.setdefault(typ, []).append(val)

        self.component_values = component_values

    def write(self, content, role=None):
        self.template_instance.add_component(dcc.Markdown(content), role=role)

    def _get_next_index_and_value(self, kind, default):
        index = self.indexes.get(kind, 0)
        if index < len(self.component_values.get(kind, [])):
            value = self.component_values[kind][index]
        else:
            value = default

        # Increment index for component type
        self.indexes[kind] = index + 1

        return index, value

    def checkbox(self, label, role=None):
        index, value = self._get_next_index_and_value("checkbox", [])
        self.template_instance.add_checkbox(option=label, value=value, role=role, name=index)
        return bool(value)

    def dropdown(self, options, optional=False, role=None):
        if isinstance(options[0], dict):
            default = options[0]["value"]
        else:
            default = options[0]

        index, value = self._get_next_index_and_value("dropdown", default)
        self.template_instance.add_dropdown(options=options, value=value, optional=optional, role=role, name=index)
        return value

    @property
    def layout(self):
        return self.template_instance.layout


def st_callback(app, fn, template=None):
    if template is None:
        template = FlatDiv()

    # Let template class configure app
    template.configure_app(app)

    # Handle wrapping output Div in app wrapper
    full = template.kwargs.get("full", True)

    # Build template instance
    template_instance = template.instance()

    output = html.Div(id="output-div")

    @app.callback(
        Output("output-div", "children"),
        [Input(build_component_pattern(), "value")]
    )
    def dash_callback(_):
        inputs_list = dash.callback_context.inputs_list
        template_instance = template.instance(full=False)
        st = ST(inputs_list, template_instance)
        fn(st)
        return st.layout

    if full:
        output = template_instance.maybe_wrap_layout(output)

    return output
