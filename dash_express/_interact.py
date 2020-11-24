import inspect
from dash.dependencies import Input, Output
import dash_html_components as html

from layouts.dbc import DbcSidebarLayout
from .layouts.util import build_id
from dash.development.base_component import Component


def interact(component_layout=None, labels=None):
    if component_layout is None:
        component_layout = DbcSidebarLayout(title="Dash Express App")

    if labels is None:
        labels = {}

    def decorator(f):
        component_layout.fn = f
        param_defaults = {}
        signature = inspect.signature(f)
        for param_name, param in signature.parameters.items():
            default = param.default
            if default is param.empty:
                raise ValueError(
                    f"Argument {param_name} must have a default value"
                )
            param_defaults[param_name] = default

        inputs = []
        for arg, pattern in param_defaults.items():
            prop_name = "value"
            label = labels.get(arg, arg)
            component_id = build_id(prefix=arg)

            # Expand tuple of (component, prop_name)
            if (isinstance(pattern, tuple) and
                    len(pattern) == 2 and
                    isinstance(pattern[0], Component)):
                pattern, prop_name = pattern

            if isinstance(pattern, list):
                options = pattern
                component_layout.add_dropdown(
                    options=options, id=component_id, label=label
                )
            elif isinstance(pattern, tuple):
                if len(pattern) == 2:
                    minimum, maximum = pattern
                    step = None
                elif len(pattern) == 3:
                    minimum, maximum, step = pattern
                else:
                    raise ValueError("Tuple default must have length 2 or 3")

                component_layout.add_slider(
                    min=minimum, max=maximum, step=step, id=component_id, label=label
                )
            elif isinstance(pattern, str):
                component_layout.add_input(
                    initial_value=pattern, id=component_id, label=label
                )
            elif isinstance(pattern, Component):
                if not getattr(pattern, "id", None):
                    pattern.id = component_id
                else:
                    component_id = pattern.id
                component_layout.add_component(pattern, kind="input", label=label)
            else:
                raise Exception("unknown pattern for " + arg)

            inputs.append(Input(component_id, prop_name))

        # For now, all output placed as children of Div
        component_layout.add_component(html.Div(id="output"), kind="output")
        output = Output("output", "children")

        # Register callback
        component_layout.app.callback(output, inputs)(f)

        return component_layout

    return decorator
