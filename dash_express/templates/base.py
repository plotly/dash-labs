from functools import wraps, update_wrapper
from dash.dependencies import Input, Output, MATCH, ALL
import dash_html_components as html
import dash_core_components as dcc
from dash.exceptions import PreventUpdate

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
    def __init__(self, label_prop, full=True):
        # Maybe this is a TemplateBuilder class with options and a .template()
        # method that build template that has the
        self.full = full
        self.label_prop = label_prop
        self._components = dict(input=[], output=[])

    def add_component(self, component, role=None, label=None):
        """
        component id should have been created with build_component_id
        """
        # Validate / infer input_like and output_like
        if role is None:
            # Default kind to output for graphs, and input for everythig else
            if component.__class__.__name__ == "Graph":
                role = "output"
            else:
                role = "input"

        if label:
            label_name = str(component.id["name"]) + "-label"
            if "{value" in label:
                # Callback to update label
                initial_value = label.format(value=getattr(component, "value", ""))

                # Build id for label
                label_id = build_id(
                    kind="formatted_label", name=label_name,
                    label_link=component.id["id"],
                    label_link_prop="value",
                    format_string=label,
                )

                # Update component id's label link
                component.id["label_link"] = component.id["id"]
                component.id["label_link_prop"] = "value"
            else:
                initial_value = label
                label_id = build_id(kind="label", name=label_name)

            layout_component, label_value_prop = \
                self.build_labeled_component(component, label_id, initial_value=initial_value)
        else:
            layout_component = component

        self._components[role].append(layout_component)

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
            id=build_component_id(kind="dropdown", name=name),
            options=options,
            clearable=clearable,
            value=value,
            **filter_kwargs(**kwargs)
        )

    def add_dropdown(self, options, value=None, optional=False, role="input", label=None, name=None, **kwargs):
        component = self.build_dropdown(options, value=value, name=name, **kwargs)
        if optional:
            component = self.build_optional_component(component)
        self.add_component(component, role=role, label=label)
        return component

    @classmethod
    def build_slider(cls, min, max, step=None, value=None, name=None, **kwargs):
        return dcc.Slider(
            id=build_component_id(kind="slider", name=name),
            min=min,
            max=max,
            value=value if value is not None else min,
            className="dcc-slider",
            **filter_kwargs(step=step, **kwargs)
        )

    def add_slider(self, min, max, step=None, value=None, optional=False, role="input", label=None, name=None, **kwargs):
        component = self.build_slider(min, max, step=step, value=value, name=name, **kwargs)
        if optional:
            component = self.build_optional_component(component)
        self.add_component(component, role=role, label=label)
        return component

    @classmethod
    def build_input(cls, value=None, name=None, **kwargs):
        return dcc.Input(
            id=build_component_id(kind="input", name=name),
            value=value,
            **filter_kwargs(**kwargs)
        )

    def add_input(self, value=None, role="input", label=None, name=None, **kwargs):
        component = self.build_input(value=value, name=name, **kwargs)
        self.add_component(component, role=role, label=label)
        return component

    @classmethod
    def build_checkbox(cls, option, value=None, name=None, **kwargs):
        if isinstance(option, str):
            option = {"label": option, "value": option}

        return dcc.Checklist(
            id=build_component_id(kind="checkbox", name=name),
            options=[option],
            value=value if value is not None else option["value"],
            **filter_kwargs(**kwargs)
        )

    def add_checkbox(self, option, value=None, role="input", label=None, name=None, **kwargs):
        component = self.build_checkbox(option, value=value, name=name, **kwargs)
        self.add_component(component, role=role, label=label)
        return component

    @classmethod
    def build_graph(cls, figure, name=None, **kwargs):
        return dcc.Graph(
            id=build_component_id(kind="graph", name=name),
            figure=figure,
            **filter_kwargs(**kwargs)
        )

    def add_graph(self, figure, role="output", label=None, name=None, **kwargs):
        component = self.build_graph(figure, name=name, **kwargs)
        self.add_component(component, role=role, label=label)
        return component

    @property
    def layout(self):
        layout = self._perform_layout()
        layout = self.maybe_wrap_layout(layout)
        return layout

    def _perform_layout(self):
        raise NotImplementedError

    def maybe_wrap_layout(self, layout):
        return layout

    @classmethod
    def build_optional_component(self, component, enabled=True):
        return component

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


class BaseTemplate:
    _template_instance_cls = BaseTemplateInstance
    _label_value_prop = "children"
    _inline_css = """
        <style>
        .dcc-slider {
            padding: 12px 20px 12px 20px !important;
            border: 1px solid #ced4da;
            border-radius: .25rem;
         }
        </style>"""

    @classmethod
    def _configure_label_formatting_callbacks(cls, app):
        # Pattern matching callback for labels with {value} formatting
        for value_prop in ["value", "children", "date", "data"]:
            @app.callback(
                Output(
                    {"id": ALL, "label_link": MATCH, 'kind': "formatted_label", "name": ALL,
                     "format_string": ALL, "label_link_prop": value_prop},
                    cls._label_value_prop
                ),
                [Input(build_component_pattern(label_link=MATCH, label_link_prop=value_prop), value_prop)],
            )
            def update_label(v):
                # Unwrap single element v due to pattern matching callback
                ctx = dash.callback_context
                format_string = ctx.outputs_list[0]["id"]["format_string"]
                v = v[0]
                # v = None
                if v is None:
                    return ["Disabled"]
                else:
                    return [format_string.format(value=v)]

    @classmethod
    def _configure_index_str(cls, app):
        app.index_string = app.index_string.replace("{%css%}", "{%css%}" + cls._inline_css)

    @classmethod
    def _configure_disabel_checkboxes(cls, app):
        @app.callback(
            Output(
                build_component_pattern(disable_link=MATCH, disable_link_prop="checked"),
                "disabled",
            ),
            [Input(
                build_component_pattern(disable_link=MATCH, disable_link_prop="disabled", kind="disable-checkbox"),
                # {"id": ALL, "disable_link": MATCH, "kind": "disable-checkbox", "name": ALL, "disable_link_prop": "checked"},
                "checked"
            )]
        )
        def update_disable_checkboxes(checked):
            ctx = dash.callback_context
            print(ctx.inputs_list)
            print(ctx.outputs_list)
            print(checked)
            print("")
            if checked is None:
                return PreventUpdate
            return [not bool(checked[0])]

    @classmethod
    def configure_app(cls, app):
        # TODO: use locking to ensure that we only do this once per app.
        cls._configure_label_formatting_callbacks(app)
        cls._configure_index_str(app)
        cls._configure_disabel_checkboxes(app)

    @classmethod
    def all_component_ids(cls):
        return Input(
            {"id": ALL, "kind": ALL, "name": ALL, "link": ALL, "link_source_prop": ALL},
            "value"
        )

    def __init__(self, **kwargs):
        self.kwargs = kwargs

    def instance(self, **kwargs):
        combined_kwargs = dict(self.kwargs, **kwargs)
        return self._template_instance_cls(label_prop=self._label_value_prop, **combined_kwargs)

    # Methods designed to be overridden by subclasses
    @classmethod
    def build_dropdown(cls, options, value=None, **kwargs):
        return cls._template_instance_cls.build_dropdown(options, value=value, **kwargs)

    @classmethod
    def build_slider(cls, min, max, step=None, value=None, **kwargs):
        return cls._template_instance_cls.build_slider(
            min, max, step=step, value=value, **kwargs
        )

    @classmethod
    def build_input(cls, value=None, **kwargs):
        return cls._template_instance_cls.build_input(value=value, **kwargs)

    @classmethod
    def build_checkbox(cls, options, value=None, **kwargs):
        return cls._template_instance_cls.build_checkbox(options, value=value, **kwargs)

    @classmethod
    def build_graph(cls, figure, **kwargs):
        return cls._template_instance_cls.build_graph(figure, **kwargs)
