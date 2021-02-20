import sys
from typing import Union

import dash_html_components as html
import dash_core_components as dcc
import dash_table  # noqa: Needs table initialization
from collections import OrderedDict
import datetime

from dash.development.base_component import Component

from dash_express.util import filter_kwargs, build_id, insert_into_ordered_dict
from dash_express.dependency import Input, Output, State
from dataclasses import dataclass


@dataclass(frozen=True)
class ArgumentComponents:
    arg_component: Component
    arg_props: Union[str, tuple, dict]
    label_component: Component
    label_props: Union[str, tuple, dict]
    container_component: Component
    container_props: Union[str, tuple, dict]


class BaseTemplate:
    _label_value_prop = "children"
    _inline_css = None
    _valid_roles = ("input", "output")

    def __init__(self):
        # Maybe this is a TemplateBuilder class with options and a .template()
        # method that build template that has the
        self.roles = {role: OrderedDict() for role in self._valid_roles}

    @classmethod
    def _add_class_to_component(cls, component):
        if isinstance(component, (dcc.Slider, dcc.RangeSlider)) and not getattr(
            component, "className", None
        ):
            component.className = "dcc-slider"

    @classmethod
    def build_parameter_components(
        cls, component, value_property=(), label=None, containered=True
    ):
        # Get reference to dependency class object for role
        arg_component = component
        arg_props = value_property

        if label:
            initial_value = label
            container_component, container_props, label, label_props = \
                cls.build_labeled_component(
                    arg_component, initial_value=initial_value
                )
            label_component = label
            label_props = label_props
        elif containered:
            label_component = None
            label_props = None
            container_component, container_props = cls.build_containered_component(
                arg_component
            )
        else:
            label_component, label_props = None, None
            container_component, container_props = arg_component, arg_props

        # container_component = container_cp.component
        # container_props = container_cp.props
        return ArgumentComponents(
            arg_component=arg_component,
            arg_props=arg_props,
            label_component=label_component,
            label_props=label_props,
            container_component=container_component,
            container_props=container_props,
        )

    def add_component(
        self,
        component,
        value_property=(),
        role="input",
        label=None,
        containered=True,
        name=None,
        before=None,
        after=None,
    ):
        """
        component id should have been created with build_component_id
        """
        if role not in self._valid_roles:
            raise ValueError(
                "Invalid role {role} provided for template of type {typ}\n"
                "    Supported roles: {roles}".format(
                    role=repr(role), typ=type(self), roles=self._valid_roles
                )
            )

        self._add_class_to_component(component)

        param_components = self.build_parameter_components(
            component,
            value_property=value_property,
            label=label,
            containered=containered,
        )

        self.roles[role] = insert_into_ordered_dict(
            odict=self.roles[role],
            value=param_components,
            key=name,
            before=before,
            after=after,
        )
        return param_components

    @classmethod
    def infer_output_component_from_value(cls, v):
        """
        This is run for the value of the `children` property of any component type.

        For compatibility, it should only convert non-json values to components.
        It should not alter strings, lists (except for recursion), or dicts.
        """
        from plotly.graph_objects import Figure

        if isinstance(v, list):
            # Process lists recursively
            return [cls.infer_output_component_from_value(el) for el in v]

        # Check if pandas is already imported. Do this instead of trying to import so
        # we don't pay the time hit of importing pandas
        if "pandas" in sys.modules:
            pd = sys.modules["pandas"]
        else:
            pd = None

        name = "callback_output"

        component_id = build_id(name=name)
        if isinstance(v, Figure):
            return cls._graph_class()(figure=v, id=component_id)
        elif pd is not None and isinstance(v, pd.DataFrame):
            return cls._datatable_class()(
                id=component_id,
                columns=[{"name": i, "id": i} for i in v.columns],
                data=v.to_dict('records'),
                page_size=15,
            )
        return v

    def get_containers(self, roles=None):
        if roles is None:
            roles = self._valid_roles
        elif isinstance(roles, str):
            roles = [roles]

        containers = []
        for role in roles:
            for pc in self.roles.get(role, {}).values():
                containers.append(pc.container_component)

        return containers

    def layout(self, app, full=True):
        # Build structure
        layout = self._perform_layout()
        if full:
            layout = self._wrap_layout(layout)

        # Configure app props like CSS
        self._configure_app(app)

        return layout

    # Methods below this comment are designed to be customized by template subclasses
    def _perform_layout(self):
        """
        Build the full layout, with the exception of any special top-level components
        added by `_wrap_layout`.

        :return:
        """
        raise NotImplementedError

    @classmethod
    def _wrap_layout(cls, layout):
        """
        Optionall wrap layout in a top-level component (e.g. Ddk.App or dbc.Container)
        :param layout:
        :return:
        """
        return layout

    def _configure_app(self, app):
        """
        configure application object.

        e.g. install CSS / external stylsheets
        """
        if self._inline_css and self._inline_css not in app.index_string:
            new_css = "\n<style>{}</style>\n".format(self._inline_css)
            app.index_string = app.index_string.replace("{%css%}", "{%css%}" + new_css)

    @classmethod
    def build_labeled_component(cls, component, initial_value):
        # Subclass could use bootstrap or ddk
        label_id = build_id("label")
        label = html.Label(id=label_id, children=initial_value)
        container_id = build_id("container")
        container = html.Div(
            id=container_id,
            style={"padding-top": 10},
            children=[
                label,
                html.Div(style={"display": "block"}, children=component),
            ],
        )
        return container, "children", label, "children"

    @classmethod
    def build_containered_component(cls, component):
        """
        Alternative to bulid_labeled_component for use without label, but for
        Unitform spacing with it
        """
        container_id = build_id("container")
        container = html.Div(
            id=container_id,
            style={"padding-top": 10},
            children=[
                html.Div(style={"display": "block"}, children=component),
            ],
        )
        return container, "children"

    # Component dependency constructors
    @classmethod
    def markdown(
            cls, children=None,
            label=Component.UNDEFINED, role=Component.UNDEFINED,
            component_property="children", kind=Output, id=None, opts=None
    ):
        return kind(
            dcc.Markdown(**filter_kwargs(opts, children=children, id=id)),
            component_property=component_property, label=label, role=role
        )

    @classmethod
    def textarea(
            cls, value=None,
            label=Component.UNDEFINED, role=Component.UNDEFINED,
            component_property="value", kind=Input, id=None, opts=None
    ):
        return kind(
            dcc.Textarea(**filter_kwargs(opts, value=value, id=id)),
            component_property=component_property, label=label, role=role
        )

    @classmethod
    def button(
            cls, children, label=Component.UNDEFINED, role=Component.UNDEFINED,
            component_property="n_clicks", kind=Input, id=None, opts=None
    ):
        return kind(
            html.Button(children=children, **filter_kwargs(opts, id=id)),
            component_property=component_property, label=label, role=role
        )

    @classmethod
    def dropdown(
            cls, options, value=Component.UNDEFINED, clearable=False,
            label=Component.UNDEFINED, role=Component.UNDEFINED,
            component_property="value", kind=Input, id=None, opts=None
    ):
        if isinstance(options, list) and options and not isinstance(options[0], dict):
            options = [{"value": opt, "label": opt} for opt in options]

        # Set starting value if dropdown is not clearable
        if value is Component.UNDEFINED and options and not clearable:
            value = options[0]["value"]

        return kind(
            dcc.Dropdown(options=options, **filter_kwargs(
                opts, value=value, id=id, clearable=clearable)),
            component_property=component_property, label=label, role=role
        )

    @classmethod
    def slider(
            cls, min, max, value=Component.UNDEFINED, step=None,
            label=Component.UNDEFINED, role=Component.UNDEFINED,
            component_property="value", kind=Input, id=None, opts=None
    ):
        tooltip = (opts or {}).pop(
            "tooltip", {"placement": "bottom", "always_visible": True}
        )

        if value is Component.UNDEFINED:
            value = min

        return kind(
            dcc.Slider(
                min=min, max=max,
                **filter_kwargs(opts,  tooltip=tooltip, step=step, value=value, id=id)
            ),
            component_property=component_property, label=label, role=role
        )

    @classmethod
    def input(
            cls, value=None,
            label=Component.UNDEFINED, role=Component.UNDEFINED,
            component_property="value", kind=Input, id=None, opts=None
    ):
        return kind(
            dcc.Input(value=value, **filter_kwargs(opts, id=id)),
            component_property=component_property, label=label, role=role
        )

    @classmethod
    def checklist(
            cls, options, value=None,
            label=Component.UNDEFINED, role=Component.UNDEFINED,
            component_property="value", kind=Input, id=None, opts=None
    ):
        if isinstance(options, list) and options and not isinstance(options[0], dict):
            options = [{"value": opt, "label": opt} for opt in options]

        return kind(
            dcc.Checklist(options=options, **filter_kwargs(opts, value=value, id=id)),
            component_property=component_property, label=label, role=role
        )

    @classmethod
    def _graph_class(cls):
        return dcc.Graph

    @classmethod
    def graph(
            cls, figure=None, config=None,
            label=Component.UNDEFINED, role=Component.UNDEFINED,
            component_property="figure", kind=Output, id=None, opts=None
    ):
        return kind(
            cls._graph_class()(**filter_kwargs(opts, figure=figure, config=config, id=id)),
            component_property=component_property, label=label, role=role
        )

    @classmethod
    def _datatable_class(cls):
        from dash_table import DataTable
        return DataTable

    @classmethod
    def date_picker_single(
            cls, date=None,
            label=Component.UNDEFINED, role=Component.UNDEFINED,
            component_property="date", kind=Input, id=None, opts=None
    ):
        if isinstance(date, datetime.date):
            date = date.isoformat()

        return kind(
            dcc.DatePickerSingle(
                date=date, **filter_kwargs(opts, id=id)
            ),
            component_property=component_property, label=label, role=role
        )

    @classmethod
    def date_picker_range(
            cls, start_date=None, end_date=None,
            label=Component.UNDEFINED, role=Component.UNDEFINED,
            component_property=("start_date", "end_date"), kind=Input, id=None, opts=None
    ):

        if isinstance(start_date, datetime.date):
            start_date = start_date.isoformat()
        if isinstance(end_date, datetime.date):
            end_date = end_date.isoformat()

        return kind(
            dcc.DatePickerRange(
                start_date=start_date, end_date=end_date, **filter_kwargs(opts, id=id)
            ),
            component_property=component_property, label=label, role=role
        )
