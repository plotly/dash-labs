from functools import wraps, update_wrapper
from dash.dependencies import Input, Output, State
import dash_html_components as html
import dash_core_components as dcc
from dash_express.layouts.util import build_id, filter_kwargs
import dash


class ComponentLayout:
    def __init__(self, app=None, name=None, fn=None, set_layout=True, **kwargs):
        self._components = dict(input=[], output=[])

        if app is None:
            self.app = dash.Dash(name=name)
        else:
            self.app = app

        # Assign function if instance is acting as a function wrapper
        self.fn = fn
        self.set_layout = set_layout

    @property
    def fn(self):
        return self._fn

    @fn.setter
    def fn(self, val):
        self._fn = val
        if val is not None:
            update_wrapper(self, val)

    def run_server(self, *args, **kwargs):
        self.app.run_server(*args, **kwargs)

    def __call__(self, *args, **kwargs):
        if self.fn:
            return self.fn(*args, **kwargs)
        else:
            raise ValueError(f"{self.__class__.__name__} instance is not callable")

    def add_component(self, component, kind=None, label=None, **kwargs):
        # Validate / infer input_like and output_like
        if kind is None:
            # Default kind to output for graphs, and input for everythig else
            if component.__class__.__name__ == "Graph":
                kind = "output"
            else:
                kind = "input"

        if label:
            if "{value" in label:
                # Callback to update label
                initial_value = label.format(value=getattr(component, "value", ""))
                dynamic_label = True
            else:
                initial_value = label
                dynamic_label = False

            label_id = f"{component.id}-label"
            layout_component, label_value_prop = \
                self.build_labeled_input(component, label_id, initial_value=initial_value)

            if dynamic_label:
                @self.app.callback(
                    Output(label_id, label_value_prop), [Input(component.id, "value")]
                )
                def update_label(v, label=label):
                    return label.format(value=v)
        else:
            layout_component = component

        self._components[kind].append(layout_component)

        if self.set_layout:
            self.app.layout = self.layout()

    # Methods designed to be overridden by subclasses
    def add_dropdown(self, options, value=None, id=None, kind="input", **kwargs):
        # Bootstrap dbc.Select
        if not options:
            raise ValueError("Options may not be empty")

        if isinstance(options[0], str):
            options = [{"label": opt, "value": opt} for opt in options]

        print("dropdown value", value)
        component = dcc.Dropdown(
            id=build_id(id, "dropdown"),
            options=options,
            clearable=False,
            value=value if value is not None else options[0]["value"]
        )
        self.add_component(component, kind=kind, **kwargs)
        return component

    def add_slider(self, min, max, step=None, value=None, id=None, kind="input", **kwargs):
        component = dcc.Slider(
            id=build_id(id, "slider"),
            min=min,
            max=max,
            value=value if value is not None else min,
            **filter_kwargs(step=step)
        )
        self.add_component(component, kind=kind, **kwargs)
        return component

    def add_input(self, value=None, id=None, kind="input", **kwargs):
        component = dcc.Input(
            id=build_id(id, "input"),
            value=value,
        )
        self.add_component(component, kind=kind, **kwargs)
        return component

    def add_checklist(self, options, value=None, id=None, kind="input", **kwargs):
        component = dcc.Checklist(
            id=id,
            options=options,
            value=value if value is not None else options[0]["value"]
        )
        self.add_component(component, kind=kind, **kwargs)
        return component

    # def add_graph(self, figure, config, id=None, kind="output", **kwargs):
    #     component = dcc.Graph(
    #         id=build_id(id, "graph"),
    #         figure=figure
    #     )

    def layout(self, full=True, assign=True):
        layout = self._perform_layout()
        if full:
            layout = self._app_wrapper(layout)

        return layout

    def _perform_layout(self):
        raise NotImplementedError

    def _app_wrapper(self, layout):
        return layout

    def build_labeled_input(self, component, label_id, initial_value):
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
