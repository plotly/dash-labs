from functools import wraps, update_wrapper
from dash.dependencies import Input, Output, MATCH, ALL
import dash_html_components as html
import dash_core_components as dcc
import re

from dash_express.templates.util import build_id, filter_kwargs, build_component_id, \
    build_component_pattern
import dash

dx_index = """<!DOCTYPE html>
<html>
    <head>
        {%metas%}
        <title>{%title%}</title>
        {%favicon%}
        {%css%}
    </head>
    <body>
        {%app_entry%}
        <footer>
            {%config%}
            {%scripts%}
            {%renderer%}
        </footer>
    </body>
</html>"""


class BaseTemplateInstance:
    _label_value_prop = "children"
    _inline_css = None

    def __init__(self, full=True):
        # Maybe this is a TemplateBuilder class with options and a .template()
        # method that build template that has the
        self.full = full
        self._components = dict(input=[], output=[])
        self._dynamic_label_callback_args = []
        self._disable_component_callback_args = []

    @classmethod
    def _style_class_component(cls, component):
        if (isinstance(component, (dcc.Slider, dcc.RangeSlider))
                and not getattr(component, "className", None)):
            component.className = "dcc-slider"

    def add_component(self, component, value_prop, role=None, label=None, optional=False):
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
            layout_component, checkbox_id, checkbox_prop = self.build_optional_component(component)
            optional_dependency = Dependency(checkbox_id, checkbox_prop)
            dependencies.append(optional_dependency)

            self._disable_component_callback_args.append([
                Output(component.id, "disabled"),
                [optional_dependency]
            ])
            # Value function
            dependency_fn = lambda val, enabled: val if enabled else None
        else:
            optional_dependency = None
            dependency_fn = None
            layout_component = component

        if label:
            label_name = str(component.id["name"]) + "-label"
            if not isinstance(label, str) or "{value" in label:
                # Callback to update label
                value = getattr(component, value_prop, "")
                if isinstance(label, str):
                    initial_value = label.format(value=value)
                else:
                    initial_value = label(value)

                # Build id for label
                label_id = build_id(
                    kind="formatted_label", name=label_name,
                )

                # Figure out callback arguments for updating label
                update_label_inputes = [Input(component.id, value_prop)]
                if optional_dependency is not None:
                    update_label_inputes.append(optional_dependency)

                self._dynamic_label_callback_args.append([
                    Output(label_id, self._label_value_prop),
                    update_label_inputes,
                    dependency_fn,
                    label,
                ])
            else:
                initial_value = label
                label_id = build_id(kind="label", name=label_name)

            layout_component, label_value_prop = \
                self.build_labeled_component(layout_component, label_id, initial_value=initial_value)

        self._components[role].append(layout_component)

        dependencies.insert(0, Dependency(component.id, value_prop))

        return dependencies, dependency_fn

    _dropdown_value_prop = "value"
    _slider_value_prop = "value"
    _input_value_prop = "value"
    _checklist_value_prop = "value"

    # Methods designed to be overridden by subclasses
    @classmethod
    def build_dropdown(cls, options, value=None, clearable=False, name=None, **kwargs):
        if not options:
            raise ValueError("Options may not be empty")

        if isinstance(options[0], str):
            options = [{"label": opt, "value": opt} for opt in options]

        if value is None and clearable is False:
            value = options[0]["value"]

        return dcc.Dropdown(
            id=build_id(kind="dropdown", name=name),
            options=options,
            clearable=clearable,
            value=value,
            **filter_kwargs(**kwargs)
        )

    def add_dropdown(self, options, value=None, role="input", label=None, name=None, optional=False, **kwargs):
        component = self.build_dropdown(options, value=value, name=name, **kwargs)
        # if optional:
        #     component = self.build_optional_component(component)
        return self.add_component(component, role=role, label=label, value_prop=self._dropdown_value_prop, optional=optional)

    @classmethod
    def build_slider(cls, min, max, step=None, value=None, name=None, **kwargs):
        return dcc.Slider(
            id=build_id(kind="slider", name=name),
            min=min,
            max=max,
            value=value if value is not None else min,
            **filter_kwargs(step=step, **kwargs)
        )

    def add_slider(self, min, max, step=None, value=None, role="input", label=None, name=None, optional=False, **kwargs):
        component = self.build_slider(min, max, step=step, value=value, name=name, **kwargs)
        return self.add_component(component, role=role, label=label, optional=optional, value_prop=self._slider_value_prop)

    @classmethod
    def build_input(cls, value=None, name=None, **kwargs):
        return dcc.Input(
            id=build_id(kind="input", name=name),
            value=value,
            **filter_kwargs(**kwargs)
        )

    def add_input(self, value=None, role="input", label=None, name=None, optional=False, **kwargs):
        component = self.build_input(value=value, name=name, **kwargs)
        return self.add_component(component, role=role, label=label, optional=optional, value_prop=self._input_value_prop)

    @classmethod
    def build_checkbox(cls, option, value=None, name=None, **kwargs):
        if isinstance(option, str):
            option = {"label": option, "value": option}

        return dcc.Checklist(
            id=build_id(kind="checkbox", name=name),
            options=[option],
            value=value if value is not None else option["value"],
            **filter_kwargs(**kwargs)
        )

    def add_checkbox(self, option, value=None, role="input", label=None, name=None, optional=False, **kwargs):
        component = self.build_checkbox(option, value=value, name=name, **kwargs)
        return self.add_component(component, role=role, label=label, optional=optional, value_prop=self._checklist_value_prop)

    @classmethod
    def build_graph(cls, figure, name=None, **kwargs):
        return dcc.Graph(
            id=build_id(kind="graph", **filter_kwargs(name=name)),
            figure=figure,
            **filter_kwargs(**kwargs)
        )

    @classmethod
    def Graph(self, figure, **kwargs):
        return self.build_graph(figure)

    def add_graph(self, figure, role="output", label=None, name=None, **kwargs):
        component = self.build_graph(figure, name=name, **kwargs)
        return self.add_component(component, role=role, label=label, value_prop="figure")

    @classmethod
    def _configure_app(cls, app):
        if cls._inline_css:
            app.index_string = app.index_string.replace(
                "{%css%}", "{%css%}" + cls._inline_css
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

    @classmethod
    def build_optional_component(self, component, enabled=True):
        raise NotImplementedError

    @classmethod
    def build_labeled_component(cls, component, label_id, initial_value):
        # Subclass could use bootstrap or ddk
        layout_component = html.Div(
            style={"padding-top": 10},
            children=[
                html.Label(id=label_id, children=initial_value),
                html.Div(
                    style={"display": "block"},
                    children=component
                ),
            ]
        )
        return layout_component, "children"
