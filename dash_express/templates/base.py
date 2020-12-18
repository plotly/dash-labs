from functools import wraps, update_wrapper
from dash.dependencies import Input, Output, MATCH, ALL
import dash_html_components as html
import dash_core_components as dcc
from dash_express.templates.util import build_id, filter_kwargs, build_component_id
import dash


class BaseTemplate:
    def __init__(self, full=True):
        # Maybe this is a TemplateBuilder class with options and a .template()
        # method that build template that has the
        self.full = full
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
            if "{value" in label:
                # Callback to update label
                initial_value = label.format(value=getattr(component, "value", ""))
                label_id = build_id(kind="formatted_label")
                label_id.update(
                    {"link": component.id["id"], "format_string": label, "link_source_prop": "value"}
                )
                component.id["link"] = component.id["id"]
                component.id["link_source_prop"] = "value"
            else:
                initial_value = label
                label_id = build_id(kind="label")

            layout_component, label_value_prop = \
                self.build_labeled_component(component, label_id, initial_value=initial_value)
        else:
            layout_component = component

        self._components[role].append(layout_component)

    # Methods designed to be overridden by subclasses
    @classmethod
    def build_dropdown(cls, options, value=None, name=None, **kwargs):
        if not options:
            raise ValueError("Options may not be empty")

        if isinstance(options[0], str):
            options = [{"label": opt, "value": opt} for opt in options]

        return dcc.Dropdown(
            id=build_component_id(kind="dropdown", name=name),
            options=options,
            clearable=False,
            value=value if value is not None else options[0]["value"],
            **filter_kwargs(**kwargs)
        )

    def add_dropdown(self, options, value=None, role="input", label=None, name=None, **kwargs):
        component = self.build_dropdown(options, value=value, name=name, **kwargs)
        self.add_component(component, role=role, label=label)
        return component

    @classmethod
    def build_slider(cls, min, max, step=None, value=None, name=None, **kwargs):
        return dcc.Slider(
            id=build_component_id(kind="slider", name=name),
            min=min,
            max=max,
            value=value if value is not None else min,
            **filter_kwargs(step=step, **kwargs)
        )

    def add_slider(self, min, max, step=None, value=None, role="input", label=None, name=None, **kwargs):
        component = self.build_slider(min, max, step=step, value=value, name=name, **kwargs)
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
        if self.full:
            layout = self._app_wrapper(layout)

        return layout

    def _perform_layout(self):
        raise NotImplementedError

    def _app_wrapper(self, layout):
        return layout

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


class BaseTemplateBuilder:
    _template_cls = BaseTemplate
    _label_value_prop = "children"

    @classmethod
    def _configure_label_formatting_callbacks(cls, app):
        # Pattern matching callback for labels with {value} formatting
        for value_prop in ["value", "children", "date", "data"]:
            @app.callback(
                Output(
                    {"id": ALL, "link": MATCH, 'kind': "formatted_label",
                     "format_string": ALL, "link_source_prop": value_prop},
                    cls._label_value_prop
                ),
                [Input(
                    {"id": ALL, "link": MATCH, "kind": ALL, "link_source_prop": value_prop, "name": ALL},
                    value_prop
                )]
            )
            def update_label(v):
                # Unwrap single element v due to pattern matching callback
                v = v[0]
                ctx = dash.callback_context
                format_string = ctx.outputs_list[0]["id"]["format_string"]
                return [format_string.format(value=v)]

    @classmethod
    def configure_app(cls, app):
        # TODO: use locking to ensure that we only do this once per app.
        cls._configure_label_formatting_callbacks(app)

    def __init__(self, **kwargs):
        self.kwargs = kwargs

    def instance(self):
        return self._template_cls(**self.kwargs)

    # Methods designed to be overridden by subclasses
    @classmethod
    def build_dropdown(cls, options, value=None, **kwargs):
        return cls._template_cls.build_dropdown(options, value=value, **kwargs)

    @classmethod
    def build_slider(cls, min, max, step=None, value=None, **kwargs):
        return cls._template_cls.build_slider(
            min, max, step=step, value=value, **kwargs
        )

    @classmethod
    def build_input(cls, value=None, **kwargs):
        return cls._template_cls.build_input(value=value, **kwargs)

    @classmethod
    def build_checkbox(cls, options, value=None, **kwargs):
        return cls._template_cls.build_checkbox(options, value=value, **kwargs)

    @classmethod
    def build_graph(cls, figure, **kwargs):
        return cls._template_cls.build_graph(figure, **kwargs)
