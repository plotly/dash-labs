from dash.dependencies import Input, Output
import dash_html_components as html
import dash_core_components as dcc
import re
import dash_table  # noqa: Needs table initialization
from functools import update_wrapper
from collections import OrderedDict

from dash_express.templates.util import filter_kwargs, build_component_id


class ParameterComponents:
    def __init__(
            self, name, value, value_property, label, label_property,
            enabler, enabler_property, container, container_property
    ):
        self.name = name
        self.value = value
        self.value_property = value_property
        self.label = label
        self.label_property = label_property
        self.enabler = enabler
        self.enabler_property = enabler_property
        self.container = container
        self.container_property = container_property


class CallbackComponents:
    def __init__(self, app, input, output, layout, fn=None):
        # Set properties
        self.app = app
        self.fn = fn
        self.input = input
        self.output = output
        self.layout = layout

        # wrap self to look like input function
        if self.fn is not None:
            update_wrapper(self, self.fn)

    def __call__(self, *args, **kwargs):
        if self.fn is None:
            raise ValueError("CallbackComponents instance does not wrap a function")
        return self.fn(*args, **kwargs)


class BaseTemplateInstance:
    _label_value_prop = "children"
    _inline_css = None

    def __init__(self, full=True):
        # Maybe this is a TemplateBuilder class with options and a .template()
        # method that build template that has the
        self.full = full
        self._role_param_components = dict(input=OrderedDict(), output=OrderedDict())
        self._dynamic_label_callback_args = []
        self._disable_component_callback_args = []

    @classmethod
    def _style_class_component(cls, component):
        if (isinstance(component, (dcc.Slider, dcc.RangeSlider))
                and not getattr(component, "className", None)):
            component.className = "dcc-slider"

    def add_component(self, component, value_property, name=None, role=None, label=None, optional=False):
        """
        component id should have been created with build_component_id
        """
        # Validate / infer input_like and output_like
        if role is None:
            # Default kind to output for graphs, and input for everything else
            if component.__class__.__name__ == "Graph":
                role = "output"
            else:
                role = "input"

        self._style_class_component(component)

        # Get reference to dependency class object for role
        Dependency = Input if role == "input" else Output
        dependencies = []

        if optional:
            container, container_property, enabler, enabler_property = \
                self.build_optional_component(component)
            optional_dependency = Dependency(enabler.id, enabler_property)
            dependencies.append(optional_dependency)

            self._disable_component_callback_args.append([
                Output(component.id, "disabled"),
                [optional_dependency]
            ])

            # Value function
            def dependency_fn(enabled, *args):
                if not enabled:
                    return None
                elif isinstance(value_property, list):
                    # Return as list
                    return args
                else:
                    # Return as scalar
                    return args[0]
        else:
            container, container_property = component, value_property
            enabler, enabler_property = None, None

            def dependency_fn(*args):
                if isinstance(value_property, list):
                    # Return as list
                    return args
                else:
                    # Return as scalar
                    return args[0]

        # Figure out callback arguments for updating label
        if isinstance(value_property, list):
            for prop in value_property:
                dependencies.append(Dependency(component.id, prop))
        else:
            dependencies.append(Dependency(component.id, value_property))

        if label:
            label_name = str(component.id["name"]) + "-label"
            if not isinstance(label, str) or "{value" in label:
                # TODO: only valid for role="input"?

                # Build id for label
                label_id = build_component_id(
                    kind="formatted_label", name=label_name,
                )

                # Callback to update label
                if isinstance(value_property, list):
                    value = [getattr(component, prop, "") for prop in value_property]
                else:
                    value = getattr(component, value_property, "")

                if isinstance(label, str):
                    initial_value = label.format(value=value)
                else:
                    initial_value = label(value)

                self._dynamic_label_callback_args.append([
                    Output(label_id, self._label_value_prop),
                    dependencies,
                    dependency_fn,
                    label,
                ])
            else:
                initial_value = label
                label_id = build_component_id(kind="label", name=label_name)

            container, container_property, label, label_property = \
                self.build_labeled_component(
                    container, label_id, initial_value=initial_value
                )
        else:
            label, label_property = None, None

        param_components = ParameterComponents(
            name=name,
            value=component,
            value_property=value_property,
            label=label,
            label_property=label_property,
            enabler=enabler,
            enabler_property=enabler_property,
            container=container,
            container_property = container_property,
        )

        # Use component index as name if no name provided
        if name is None:
            name = len(self._role_param_components[role])

        self._role_param_components[role][name] = param_components

        return dependencies, dependency_fn

    _dropdown_value_prop = "value"
    _slider_value_prop = "value"
    _input_value_prop = "value"
    _checklist_value_prop = "value"

    # Methods designed to be overridden by subclasses
    @classmethod
    def Button(cls, *args, id=None, **kwargs):
        return html.Button(*args, **filter_kwargs(id=id, **kwargs))

    @classmethod
    def Dropdown(cls, options, id=None, value=None, clearable=False, **kwargs):
        if not options:
            raise ValueError("Options may not be empty")

        if isinstance(options[0], str):
            options = [{"label": opt, "value": opt} for opt in options]

        if value is None and clearable is False:
            value = options[0]["value"]

        return dcc.Dropdown(
            options=options,
            clearable=clearable,
            value=value,
            **filter_kwargs(id=id, **kwargs)
        )

    def add_dropdown(self, options, value=None, name=None, role="input", label=None, optional=False, **kwargs):
        id = build_component_id(kind="dropdown", name=name)
        component = self.Dropdown(options, id=id, value=value, **kwargs)
        return self.add_component(
            component, value_property=self._dropdown_value_prop,
            name=name, role=role, label=label, optional=optional
        )

    @classmethod
    def Slider(cls, min, max, id=None, step=None, value=None, **kwargs):
        return dcc.Slider(
            min=min,
            max=max,
            value=value if value is not None else min,
            **filter_kwargs(id=id, step=step, **kwargs)
        )

    def add_slider(self, min, max, step=None, value=None, role="input", label=None, name=None, optional=False, **kwargs):
        id = build_component_id(kind="slider", name=name)
        component = self.Slider(min, max, id=id, step=step, value=value, **kwargs)
        return self.add_component(
            component, value_property=self._slider_value_prop,
            name=name, role=role, label=label, optional=optional
        )

    @classmethod
    def Input(cls, value=None, id=None, **kwargs):
        return dcc.Input(
            value=value,
            **filter_kwargs(id=id, **kwargs)
        )

    def add_input(self, value=None, role="input", label=None, name=None, optional=False, **kwargs):
        id = build_component_id(kind="input", name=name)
        component = self.Input(value=value, id=id, **kwargs)
        return self.add_component(
            component, value_property=self._input_value_prop,
            name=name, role=role, label=label, optional=optional
        )

    @classmethod
    def Checkbox(cls, option, id=id, value=None, **kwargs):
        if isinstance(option, str):
            option = {"label": option, "value": option}

        return dcc.Checklist(
            options=[option],
            value=value if value is not None else option["value"],
            **filter_kwargs(id=id, **kwargs)
        )

    def add_checkbox(self, option, value=None, role="input", label=None, name=None, optional=False, **kwargs):
        id = build_component_id(kind="checkbox", name=name)
        component = self.Checkbox(option, value=value, id=id, **kwargs)
        return self.add_component(
            component, value_property=self._checklist_value_prop,
            name=name, role=role, label=label, optional=optional
        )

    @classmethod
    def Graph(cls, figure=None, id=None, **kwargs):
        return dcc.Graph(
            **filter_kwargs(id=id, figure=figure, **kwargs)
        )

    def add_graph(self, figure, role="output", label=None, name=None, **kwargs):
        id = build_component_id(kind="graph", name=name)
        component = self.Graph(figure, id=id, **kwargs)
        return self.add_component(
            component, value_property="figure",
            name=name, role=role, label=label
        )

    @classmethod
    def DataTable(cls, *args, **kwargs):
        from dash_table import DataTable
        return DataTable(*args, **kwargs)

    def add_datatable(self, *args, name=None, role=None, label=None, **kwargs):
        id = build_component_id(kind="graph", name=name)
        component = self.DataTable(*args, id=id, **kwargs)
        return self.add_component(
            component, value_property="data", name=name, role=role, label=label
        )

    @classmethod
    def _configure_app(cls, app):
        if cls._inline_css:
            app.index_string = app.index_string.replace(
                "{%css%}", "{%css%}" + cls._inline_css
            )

    def callback_components(self, app):
        layout = self.build_layout(app)
        return CallbackComponents(
            app, input=self._role_param_components['input'],
            output=self._role_param_components['output'], layout=layout
        )

    def build_layout(self, app):
        # Build structure
        layout = self._perform_layout()
        layout = self.maybe_wrap_layout(layout)

        # Add callbacks
        for output, inputs, dependency_fn, label in self._dynamic_label_callback_args:
            @app.callback(output, inputs)
            def format_label(*args, dependency_fn=dependency_fn, label=label):

                if dependency_fn is not None:
                    val = dependency_fn(*args)
                else:
                    val = args[0]
                print(args, val)
                if isinstance(label, str):
                    if val is not None:
                        return label.format(value=val)
                    else:
                        # Replace the {value...} wildcard with "None"
                        return re.sub("{value(:[^}]*)?}", "None", label)
                else:
                    return label(val)

        # Checkboxes
        for output, inputs in self._disable_component_callback_args:
            @app.callback(output, inputs)
            def disable_component(checked):
                return not bool(checked)

        # CSS
        self._configure_app(app)

        return layout

    def _perform_layout(self):
        raise NotImplementedError

    def maybe_wrap_layout(self, layout):
        return layout

    @property
    def output_containers(self):
        return [c.container for c in self._role_param_components['output'].values()]

    @property
    def input_containers(self):
        return [c.container for c in self._role_param_components['input'].values()]

    @classmethod
    def build_optional_component(self, component, enabled=True):
        checkbox_id = build_component_id(
            kind="disable-checkbox", name=str(component.id["name"]) + "-enabled",
        )

        checklist_value = ["checked"] if enabled else []
        checkbox = dcc.Checklist(
            id=checkbox_id, options=[{"label": "", "value": "checked"}],
            value=checklist_value
        )
        checkbox_property = "value"
        container = html.Div(
            style={"display": "flex", "align-items": "center"},
            children=[
                checkbox,
                html.Div(style=dict(flex="auto"), children=component)
            ]
        )
        container_property = "children"
        return container, container_property, checkbox, checkbox_property

    @classmethod
    def build_labeled_component(cls, component, label_id, initial_value):
        # Subclass could use bootstrap or ddk
        label = html.Label(id=label_id, children=initial_value)
        container = html.Div(
            style={"padding-top": 10},
            children=[
                label,
                html.Div(
                    style={"display": "block"},
                    children=component
                ),
            ]
        )
        return container, "children", label, "children"
