import inspect
from dash.dependencies import Input, Output
import dash_html_components as html

from dash_express.templates.dbc import DbcSidebar
from dash_express.templates.util import build_id, build_component_id
from dash.development.base_component import Component


def parameterize(app, fn, params, template=None, labels=None):
    if template is None:
        template = DbcSidebar(title="Dash Express App")

    if labels is None:
        labels = {}

    # Let template class configure app
    template.configure_app(app)

    # Build template instance
    template_instance = template.instance()

    param_defaults = {}
    for param_name, param in params.items():
        param_defaults[param_name] = param

    inputs = []
    for arg, pattern in param_defaults.items():
        prop_name = "value"
        label = labels.get(arg, arg)

        # Expand tuple of (component, prop_name)
        if (isinstance(pattern, tuple) and
                len(pattern) == 2 and
                isinstance(pattern[0], Component)):
            pattern, prop_name = pattern

        if isinstance(pattern, list):
            options = pattern
            component_id = template_instance.add_dropdown(
                options=options, label=label, name=arg
            ).id
        elif isinstance(pattern, tuple):
            if len(pattern) == 2:
                minimum, maximum = pattern
                step = None
            elif len(pattern) == 3:
                minimum, maximum, step = pattern
            else:
                raise ValueError("Tuple default must have length 2 or 3")

            component_id = template_instance.add_slider(
                min=minimum, max=maximum, step=step, label=label, name=arg
            ).id
        elif isinstance(pattern, str):
            component_id = template_instance.add_input(
                value=pattern, label=label, name=arg
            ).id
        elif isinstance(pattern, Component):
            # Overwrite id
            component_id = build_component_id(kind="component", name=arg)
            pattern.id = component_id
            template_instance.add_component(pattern, role="input", label=label)
        else:
            raise Exception("unknown pattern for " + arg)

        inputs.append(Input(component_id, prop_name))

    # For now, all output placed as children of Div
    template_instance.add_component(html.Div(id="output"), role="output")
    output = Output("output", "children")

    # Register callback
    app.callback(output, inputs)(fn)

    return template_instance.layout
