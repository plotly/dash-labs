import sys
import dash_html_components as html
import dash_core_components as dcc
import dash_table  # noqa: Needs table initialization
from collections import OrderedDict
import datetime

from dash.development.base_component import Component

from dash_express import ComponentProps
from dash_express.util import filter_kwargs, build_id, insert_into_ordered_dict
from dataclasses import dataclass


@dataclass(frozen=True)
class ArgumentComponents:
    value: ComponentProps
    label: ComponentProps
    container: ComponentProps


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
        parameter_cp = component.props[value_property]
        container_cp = parameter_cp

        if label:
            initial_value = label
            container_cp, label_cp = cls.build_labeled_component(
                container_cp.component, initial_value=initial_value
            )
        elif containered:
            label_cp = None
            container_cp = cls.build_containered_component(container_cp.component)
        else:
            label_cp = None
            container_cp = parameter_cp

        return ArgumentComponents(
            value=parameter_cp,
            label=label_cp,
            container=container_cp,
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
    def infer_input_component_props_from_pattern(cls, pattern, id=None):
        if isinstance(pattern, ComponentProps):
            # Nothing to do
            return pattern
        elif isinstance(pattern, Component):
            # Default to value prop of component
            # TODO: specialize error message, explaining value is the default and how
            #       to customize with .props syntax
            return pattern.props["value"]
        elif isinstance(pattern, list):
            # Dropdown
            options = pattern

            # Normalize options
            if options and not isinstance(options[0], dict):
                options = [{"label": opt, "value": opt} for opt in options]

            # compute starting value
            if options:
                value = options[0]["value"]
            else:
                value = None
            return ComponentProps(
                cls.Dropdown(options=options, value=value, id=id),
                "value",
            )
        elif isinstance(pattern, tuple) and all(
            isinstance(el, (int, float)) for el in pattern
        ):
            if len(pattern) == 2:
                minimum, maximum = pattern
                step = None
            elif len(pattern) == 3:
                minimum, maximum, step = pattern
            else:
                raise ValueError("Tuple pattern must have length 2 or 3")

            return ComponentProps(
                cls.Slider(min=minimum, max=maximum, value=minimum, step=step, id=id),
                "value",
            )
        elif isinstance(pattern, str):
            return ComponentProps(
                cls.Input(value=pattern, id=id),
                "value",
            )
        elif isinstance(pattern, bool):
            return ComponentProps(
                cls.Checklist(
                    options=[{"label": "", "value": "checked"}],
                    value=["checked"] if pattern else [],
                    id=id,
                ),
                "value",
            )
        else:
            return None

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
            return cls.Graph(v, id=component_id)
        elif pd is not None and isinstance(v, pd.DataFrame):
            return cls.DataTable(
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
                containers.append(pc.container.component)

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
        return container.props["children"], label.props["children"]

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
        return container.props["children"]

    # Component constructors
    # These are uppercased class method to hopefully help communicate that they are
    # component constructors that don't modify the template
    @classmethod
    def Markdown(cls, children=None, id=None, **kwargs):
        return dcc.Markdown(
            # className="param-markdown",
            **filter_kwargs(children=children, id=id, **kwargs)
        )

    @classmethod
    def Button(cls, children=None, id=None, **kwargs):
        return html.Button(**filter_kwargs(children=children, id=id, **kwargs))

    @classmethod
    def Dropdown(cls, options, id=None, value=None, **kwargs):
        return dcc.Dropdown(
            options=options, **filter_kwargs(id=id, value=value, **kwargs)
        )

    @classmethod
    def Slider(cls, min, max, id=None, step=None, value=None, **kwargs):
        # Tooltip enabled by default to show slider value
        tooltip = kwargs.pop("tooltip", {"placement": "bottom", "always_visible": True})
        return dcc.Slider(
            min=min,
            max=max,
            tooltip=tooltip,
            **filter_kwargs(id=id, step=step, value=value, **kwargs),
        )

    @classmethod
    def Input(cls, value=None, id=None, **kwargs):
        return dcc.Input(value=value, **filter_kwargs(id=id, **kwargs))

    #

    @classmethod
    def Checklist(cls, options, id=None, value=None, **kwargs):
        return dcc.Checklist(
            options=options, value=value, **filter_kwargs(id=id, **kwargs)
        )

    @classmethod
    def Graph(cls, figure=None, id=None, **kwargs):
        return dcc.Graph(**filter_kwargs(id=id, figure=figure, **kwargs))

    @classmethod
    def DataTable(cls, data=None, columns=None, id=None, **kwargs):
        from dash_table import DataTable

        return DataTable(**filter_kwargs(data=data, columns=columns, **kwargs))

    @classmethod
    def DatePickerSingle(cls, date=None, id=None, **kwargs):
        if isinstance(date, datetime.date):
            date = date.isoformat()
        return dcc.DatePickerSingle(date=date, **filter_kwargs(id=id, **kwargs))

    @classmethod
    def DatePickerRange(cls, start_date=None, end_date=None, id=None, **kwargs):
        if isinstance(start_date, datetime.date):
            start_date = start_date.isoformat()
        if isinstance(end_date, datetime.date):
            end_date = end_date.isoformat()

        return dcc.DatePickerRange(
            start_date=start_date,
            end_date=end_date,
            **filter_kwargs(id=id, **kwargs),
        )
