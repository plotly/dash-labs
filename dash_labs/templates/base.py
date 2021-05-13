import sys
from typing import Union

import dash_html_components as html
import dash_core_components as dcc
import dash_table  # noqa: Needs table initialization
from collections import OrderedDict
import datetime

from dash.development.base_component import Component

from dash_labs.util import filter_kwargs, build_id, insert_into_ordered_dict
from dash_labs.dependency import Input, Output, State, DashLabsDependency
from dataclasses import dataclass


@dataclass(frozen=True)
class ArgumentComponents:
    arg_component: Component
    arg_property: Union[str, tuple, dict]
    label_component: Component
    label_property: Union[str, tuple, dict]
    container_component: Component
    container_property: Union[str, tuple, dict]


class BaseTemplate:
    """
    Base class for dash-labs templates
    """

    # The property of this template's label components that holds the label string
    _label_value_prop = "children"

    # Optional string containing css class definitions that will be enclosed in a
    # <style></style> tag and added to the app's index.html file.
    _inline_css = """
    .rc-slider-tooltip-inner {
        user-select: none;
    }
    """

    # Tuple of the roles supported by this template. Subclasses may override this
    # as a class attribute (as is the case here), or as an instance attribute if the
    # available roles are dependent on constructor arguments.
    #
    # If overriding as an instance attribute, be sure to set the value of the
    # _valid_roles attribute before calling the superclass constructor so that the
    # self._roles dict is initialized properly
    _valid_roles = ("input", "output")

    def __init__(self, app):
        self._roles = {role: OrderedDict() for role in self._valid_roles}

        # Configure app props like CSS
        if app is not None:
            self._configure_app(app)

    @property
    def roles(self):
        """
        Dictionary from role to OrderedDict of ArgumentComponents instances.

        Each component added to the template is wrapped in an ArgumentComponents
        instance and stored in the OrderedDict corresponding to the component's role

        :return: dict from roles to OrderedDict of ArgumentComponents instances
        """
        return self._roles

    @classmethod
    def build_argument_components(
        cls,
        component,
        value_property=(),
        label=None,
        label_id=None,
        role=None,
    ):
        # Get reference to dependency class object for role
        arg_component = component
        arg_props = value_property

        if label and label is not Component.UNDEFINED:
            initial_value = label
            (
                container_component,
                container_props,
                label,
                label_props,
            ) = cls.build_labeled_component(
                arg_component,
                label=initial_value,
                label_id=label_id,
                role=role,
            )
            label_component = label
            label_props = label_props
        else:
            label_component = None
            label_props = None
            container_component, container_props = cls.build_containered_component(
                arg_component,
                role=role,
            )

        return ArgumentComponents(
            arg_component=arg_component,
            arg_property=arg_props,
            label_component=label_component,
            label_property=label_props,
            container_component=container_component,
            container_property=container_props,
        )

    def add_component(
        self,
        component,
        role="input",
        label=None,
        label_id=None,
        name=None,
        component_property=None,
        before=None,
        after=None,
    ):
        """
        Add a component to the template

        :param component: The Dash component instance to add to the template
        :param role: The role of the component within the template. All templates
            support the "input" and "output" roles, but individual templates may
            support additional roles.
        :param label: (optional) A string label for the component
        :param label_id: (optional) A custom component id to use for the created
            label component (if any)
        :param name: (optional) A string name for the component. Must be unique for
            all components within the same role. If not provided, name is effectively
            the positional index of component within role.
        :param component_property: (optional) A component property to be stored in the
            ArgumentComponents instance for the added component
        :param before: (optional) String name, or positional index, of existing
            component within the same role that this component should be inserted
            before.
        :param after: (optional) String name, or positional index, of existing
            component within the same role that this component should be inserted
            after.
        :return: ArgumentComponents instance representing the component and label
            within the template
        """
        if role not in self._valid_roles:
            raise ValueError(
                "Invalid role {role} provided for template of type {typ}\n"
                "    Supported roles: {roles}".format(
                    role=repr(role), typ=type(self), roles=self._valid_roles
                )
            )

        arg_components = self.build_argument_components(
            component,
            value_property=component_property,
            label=label,
            label_id=label_id,
            role=role,
        )

        self._roles[role] = insert_into_ordered_dict(
            odict=self._roles[role],
            value=arg_components,
            key=name,
            before=before,
            after=after,
        )
        return arg_components

    def get_containers(self, roles=None):
        """
        Get list of Dash components that contain the components added to the template

        :param roles: String name of single role to include, or list of
            roles to include. If None (default), include components from all roles
        :return: flat list of container components
        """
        if roles is None:
            roles = self._valid_roles
        elif isinstance(roles, str):
            roles = [roles]

        containers = []
        for role in roles:
            for pc in self._roles.get(role, {}).values():
                containers.append(pc.container_component)

        return containers

    @property
    def children(self):
        """
        Return a component that aranges all of the components that have been added to
        the template.

        :return: Dash Component
        """
        return self._perform_layout()

    # Methods below this comment are designed to be customized by template subclasses
    # -------------------------------------------------------------------------------
    def _perform_layout(self):
        """
        Build the layout (will be provided to user as tpl.children property)

        :return: Dash Component
        """
        raise NotImplementedError

    def _configure_app(self, app):
        """
        Configure application object.

        e.g. install inline CSS / add external stylsheets
        """
        # Needs to be idempotent in case multiple templates are associated with the
        # same app
        if self._inline_css and self._inline_css not in app.index_string:
            new_css = "\n<style>{}</style>\n".format(self._inline_css)
            app.index_string = app.index_string.replace("{%css%}", "{%css%}" + new_css)

    @classmethod
    def build_labeled_component(cls, component, label, label_id=None, role=None):
        """
        Wrap input component in a labeled container

        :param component: Component to wrap
        :param label: Label string
        :param label_id: (optional) component of component that will store the label
            string
        :param role: Component role
        :return: tuple of (
            container: Dash component containing input component and label component
            container_property: Property of container component containing the input
                component
            label_component: Dash component containing the label string
            label_property: Property of label_component that stores the label string
        )
        """
        # Subclass could use bootstrap or ddk
        if not label_id:
            label_id = build_id("label")
        label_component = html.Label(id=label_id, children=label)
        container_id = build_id("container")
        container = html.Div(
            id=container_id,
            style={"padding-top": 10},
            children=[
                label_component,
                html.Div(style={"display": "block"}, children=component),
            ],
        )
        return container, "children", label_component, "children"

    @classmethod
    def build_containered_component(cls, component, role=None):
        """
        Alternative to bulid_labeled_component for use without label. Used to
        provided unitform spacing across labeled and unlabeled components

        :param component: Component to wrap in container
        :param role: Component role
        :return: tuple of (
            container: Dash component containing input component
            container_property: Property of container component containing the input
                component
        )
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

    @classmethod
    def default_output(cls, children=None):
        """
        If not Output dependency is specified in app.callback, use this component
        dependency as the output.

        Typically an html.Div, but it may be overridden by template subclasses

        :return: Dash Component
        """
        return cls.div_output(**filter_kwargs(children=children))

    # Component dependency constructors
    # ---------------------------------
    # Subclasses are welcome to override component dependency constructors, and to add
    # new constructors. The following conventions should be followed
    #
    #  1. The final underscore suffix should match the default role of the component.
    #     e.g. all of the examples below have either a _input or _output suffix, which
    #     matches the default value of the role argument.  The default suffix/role
    #     should be chosen based on whether the component is most commonly used as an
    #     input or output to a callback function.  Callers can override this behavior
    #     using the role and kind arguments.
    #
    #     If there are common uses for the component type in multiple roles,
    #     multiple methods may be defined, with a suffix for each role.
    #
    #  2. The default value of the kind argument should be consistent with the default
    #     role (e.g. kind=dl.Input for role="input" and kind=hl.Output for
    #     role="output"). The return value of the method should always match the class
    #     passed as the kind argument.
    #
    #  3. The default value of component_property should be a grouping of properties
    #     from the type of component returned that are most likely to be used as
    #     the input or output properties of the callback for that component.
    #
    #  4  The opts dict argument should be passed through as keyword arguments to the
    #     constructor of the underlying component.
    #
    #  5. The optional argument should be used to override the id of the constructed
    #     component.
    #
    #  6. The component_property, label, and role arguments should be passed through
    #     to the return dependency object.
    #
    @classmethod
    def div_output(
        cls,
        children=None,
        label=Component.UNDEFINED,
        role="output",
        component_property="children",
        kind=Output,
        id=None,
        opts=None,
    ):
        return kind(
            html.Div(**filter_kwargs(opts, children=children, id=id)),
            component_property=component_property,
            label=label,
            role=role,
        )

    @classmethod
    def markdown_output(
        cls,
        children=None,
        label=Component.UNDEFINED,
        role="output",
        component_property="children",
        kind=Output,
        id=None,
        opts=None,
    ):
        return kind(
            dcc.Markdown(**filter_kwargs(opts, children=children, id=id)),
            component_property=component_property,
            label=label,
            role=role,
        )

    @classmethod
    def textarea_input(
        cls,
        value=None,
        label=Component.UNDEFINED,
        role="input",
        component_property="value",
        kind=Input,
        id=None,
        opts=None,
    ):
        return kind(
            dcc.Textarea(**filter_kwargs(opts, value=value, id=id)),
            component_property=component_property,
            label=label,
            role=role,
        )

    @classmethod
    def button_input(
        cls,
        children,
        label=Component.UNDEFINED,
        role="input",
        component_property="n_clicks",
        kind=Input,
        id=None,
        opts=None,
    ):
        return kind(
            html.Button(children=children, **filter_kwargs(opts, id=id)),
            component_property=component_property,
            label=label,
            role=role,
        )

    @classmethod
    def dropdown_input(
        cls,
        options,
        value=Component.UNDEFINED,
        clearable=False,
        label=Component.UNDEFINED,
        role="input",
        component_property="value",
        kind=Input,
        id=None,
        opts=None,
    ):
        if isinstance(options, list) and options and not isinstance(options[0], dict):
            options = [{"value": opt, "label": opt} for opt in options]

        # Set starting value if dropdown is not clearable
        if value is Component.UNDEFINED and options and not clearable:
            value = options[0]["value"]

        return kind(
            dcc.Dropdown(
                options=options,
                **filter_kwargs(opts, value=value, id=id, clearable=clearable)
            ),
            component_property=component_property,
            label=label,
            role=role,
        )

    @classmethod
    def slider_input(
        cls,
        min,
        max,
        value=Component.UNDEFINED,
        step=None,
        tooltip=None,
        label=Component.UNDEFINED,
        role="input",
        component_property="value",
        kind=Input,
        id=None,
        opts=None,
    ):
        if tooltip is None:
            tooltip = (opts or {}).pop(
                "tooltip", {"placement": "bottom", "always_visible": True}
            )
        elif tooltip is True:
            tooltip = {"placement": "bottom", "always_visible": True}
        else:
            tooltip = None

        if value is Component.UNDEFINED:
            value = min

        return kind(
            dcc.Slider(
                min=min,
                max=max,
                **filter_kwargs(opts, tooltip=tooltip, step=step, value=value, id=id)
            ),
            component_property=component_property,
            label=label,
            role=role,
        )

    @classmethod
    def textbox_input(
        cls,
        value=None,
        label=Component.UNDEFINED,
        role="input",
        component_property="value",
        kind=Input,
        id=None,
        opts=None,
    ):
        return kind(
            dcc.Input(value=value, **filter_kwargs(opts, id=id)),
            component_property=component_property,
            label=label,
            role=role,
        )

    @classmethod
    def checklist_input(
        cls,
        options,
        value=None,
        label=Component.UNDEFINED,
        role="input",
        component_property="value",
        kind=Input,
        id=None,
        opts=None,
    ):
        if isinstance(options, list) and options and not isinstance(options[0], dict):
            options = [{"value": opt, "label": opt} for opt in options]

        if not isinstance(value, list):
            value = [value]

        return kind(
            dcc.Checklist(options=options, **filter_kwargs(opts, value=value, id=id)),
            component_property=component_property,
            label=label,
            role=role,
        )

    @classmethod
    def _graph_class(cls):
        return dcc.Graph

    @classmethod
    def graph_output(
        cls,
        figure=None,
        config=None,
        label=Component.UNDEFINED,
        role="output",
        component_property="figure",
        kind=Output,
        id=None,
        opts=None,
    ):
        return kind(
            cls._graph_class()(
                **filter_kwargs(opts, figure=figure, config=config, id=id)
            ),
            component_property=component_property,
            label=label,
            role=role,
        )

    @classmethod
    def _datatable_class(cls):
        from dash_table import DataTable

        return DataTable

    @classmethod
    def date_picker_single_input(
        cls,
        date=None,
        label=Component.UNDEFINED,
        role="input",
        component_property="date",
        kind=Input,
        id=None,
        opts=None,
    ):
        if isinstance(date, datetime.date):
            date = date.isoformat()

        return kind(
            dcc.DatePickerSingle(date=date, **filter_kwargs(opts, id=id)),
            component_property=component_property,
            label=label,
            role=role,
        )

    @classmethod
    def date_picker_range_input(
        cls,
        start_date=None,
        end_date=None,
        label=Component.UNDEFINED,
        role="input",
        component_property=("start_date", "end_date"),
        kind=Input,
        id=None,
        opts=None,
    ):

        if isinstance(start_date, datetime.date):
            start_date = start_date.isoformat()
        if isinstance(end_date, datetime.date):
            end_date = end_date.isoformat()

        return kind(
            dcc.DatePickerRange(
                start_date=start_date, end_date=end_date, **filter_kwargs(opts, id=id)
            ),
            component_property=component_property,
            label=label,
            role=role,
        )
