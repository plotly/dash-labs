from dash.dependencies import Input, Output
import dash_html_components as html
import dash_core_components as dcc
import re
import dash_table  # noqa: Needs table initialization

from dash_express.templates.util import filter_kwargs, build_component_id

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
                label_id = build_component_id(
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
                label_id = build_component_id(kind="label", name=label_name)

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

    def add_dropdown(self, options, value=None, role="input", label=None, name=None, optional=False, **kwargs):
        id = build_component_id(kind="dropdown", name=name)
        component = self.Dropdown(options, id=id, value=value, **kwargs)
        # if optional:
        #     component = self.build_optional_component(component)
        return self.add_component(component, role=role, label=label, value_prop=self._dropdown_value_prop, optional=optional)

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
        return self.add_component(component, role=role, label=label, optional=optional, value_prop=self._slider_value_prop)

    @classmethod
    def Input(cls, value=None, id=None, **kwargs):
        return dcc.Input(
            value=value,
            **filter_kwargs(id=id, **kwargs)
        )

    def add_input(self, value=None, role="input", label=None, name=None, optional=False, **kwargs):
        id = build_component_id(kind="input", name=name)
        component = self.Input(value=value, id=id, **kwargs)
        return self.add_component(component, role=role, label=label, optional=optional, value_prop=self._input_value_prop)

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
        return self.add_component(component, role=role, label=label, optional=optional, value_prop=self._checklist_value_prop)

    @classmethod
    def Graph(cls, figure=None, id=None, **kwargs):
        return dcc.Graph(
            **filter_kwargs(id=id, figure=figure, **kwargs)
        )

    def add_graph(self, figure, role="output", label=None, name=None, **kwargs):
        id = build_component_id(kind="graph", name=name)
        component = self.Graph(figure, id=id, **kwargs)
        return self.add_component(component, role=role, label=label, value_prop="figure")

    @classmethod
    def DataTable(cls, *args, **kwargs):
        from dash_table import DataTable
        return DataTable(*args, **kwargs)

    def add_datatable(self, *args, name=None, role=None, label=None, **kwargs):
        id = build_component_id(kind="graph", name=name)
        component = self.DataTable(*args, id=id, **kwargs)
        return self.add_component(component, role=role, label=label, value_prop="data")

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
        checkbox_id = build_component_id(
            kind="disable-checkbox", name=str(component.id["name"]) + "-enabled",
        )

        checklist_value = ["checked"] if enabled else []
        input_group = html.Div(
            style={"display": "flex", "align-items": "center"},
            children=[
                dcc.Checklist(id=checkbox_id,
                              options=[{"label": "", "value": "checked"}],
                              value=checklist_value),
                html.Div(style=dict(flex="auto"), children=component)
            ]
        )
        return input_group, checkbox_id, "value"

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
