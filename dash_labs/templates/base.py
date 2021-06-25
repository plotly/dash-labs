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

    # Tuple of the locations supported by this template. Subclasses should override this
    # as a class attribute (as is the case here), or as an instance attribute if the
    # available roles are dependent on constructor arguments.
    #
    # If overriding as an instance attribute, be sure to set the value of the
    # _valid_roles attribute before calling the superclass constructor so that the
    # self._roles dict is initialized properly
    _valid_locations = ()

    # Default template location for `Input` and 'State' dependencies
    _default_input_location = None

    # Default template location for `Output` dependencies
    _default_output_location = None

    def __init__(self, app):
        self._locations = {
            location: OrderedDict() for location in self._valid_locations
        }

        # Configure app props like CSS
        if app is not None:
            self._configure_app(app)

    @property
    def locations(self):
        """
        Dictionary from location to OrderedDict of ArgumentComponents instances.

        Each component added to the template is wrapped in an ArgumentComponents
        instance and stored in the OrderedDict corresponding to the component's location

        :return: dict from roles to OrderedDict of ArgumentComponents instances
        """
        return self._locations

    @classmethod
    def build_argument_components(
        cls,
        component,
        value_property=(),
        label=None,
        label_id=None,
        location=None,
    ):
        # Get reference to dependency class object for location
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
                location=location,
            )
            label_component = label
            label_props = label_props
        else:
            label_component = None
            label_props = None
            container_component, container_props = cls.build_containered_component(
                arg_component,
                location=location,
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
        location,
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
        :param location: The location of the component within the template. Individual
            templates document their supported location values in the constructor
            docstring.
        :param label: (optional) A string label for the component
        :param label_id: (optional) A custom component id to use for the created
            label component (if any)
        :param name: (optional) A string name for the component. Must be unique for
            all components within the same location. If not provided, name is effectively
            the positional index of component within location.
        :param component_property: (optional) A component property to be stored in the
            ArgumentComponents instance for the added component
        :param before: (optional) String name, or positional index, of existing
            component within the same location that this component should be inserted
            before.
        :param after: (optional) String name, or positional index, of existing
            component within the same location that this component should be inserted
            after.
        :return: ArgumentComponents instance representing the component and label
            within the template
        """
        if location not in self._valid_locations:
            raise ValueError(
                "Invalid location {location} provided for template of type {typ}\n"
                "    Supported locations: {locations}".format(
                    location=repr(location),
                    typ=type(self),
                    locations=self._valid_locations,
                )
            )

        arg_components = self.build_argument_components(
            component,
            value_property=component_property,
            label=label,
            label_id=label_id,
            location=location,
        )

        self._locations[location] = insert_into_ordered_dict(
            odict=self._locations[location],
            value=arg_components,
            key=name,
            before=before,
            after=after,
        )
        return arg_components

    def get_containers(self, locations=None):
        """
        Get list of Dash components that contain the components added to the template

        :param locations: String name of single location to include, or list of
            roles to include. If None (default), include components from all roles
        :return: flat list of container components
        """
        if locations is None:
            locations = self._valid_locations
        elif isinstance(locations, str):
            locations = [locations]

        containers = []
        for location in locations:
            for pc in self._locations.get(location, {}).values():
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
    def build_labeled_component(cls, component, label, label_id=None, location=None):
        """
        Wrap input component in a labeled container

        :param component: Component to wrap
        :param label: Label string
        :param label_id: (optional) component of component that will store the label
            string
        :param location: Component location
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
    def build_containered_component(cls, component, location=None):
        """
        Alternative to bulid_labeled_component for use without label. Used to
        provided unitform spacing across labeled and unlabeled components

        :param component: Component to wrap in container
        :param location: Component location
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
        return cls.new_div(**filter_kwargs(children=children))

    # Component dependency constructors
    # ---------------------------------
    # Subclasses are welcome to override component dependency constructors, and to add
    # new constructors. The following conventions should be followed
    #
    #  1. Methods should be prefixed by `new_`
    #
    #  2. The default value of component_property should be a grouping of properties
    #     from the type of component returned that are most likely to be used as
    #     the input or output properties of the callback for that component.
    #
    #  3. The opts dict argument should be passed through as keyword arguments to the
    #     constructor of the underlying component.
    #
    #  4. The optional argument should be used to override the id of the constructed
    #     component.
    #
    #  5. The component_property, label, and location arguments should be passed through
    #     to the return dependency object.
    #
    @classmethod
    def new_div(
        cls,
        children=None,
        label=Component.UNDEFINED,
        kind=Output,
        location=Component.UNDEFINED,
        component_property="children",
        id=None,
        opts=None,
    ):
        return kind(
            html.Div(**filter_kwargs(opts, children=children, id=id)),
            component_property=component_property,
            label=label,
            location=location,
        )

    @classmethod
    def new_markdown(
        cls,
        children=None,
        label=Component.UNDEFINED,
        kind=Output,
        location=Component.UNDEFINED,
        component_property="children",
        id=None,
        opts=None,
    ):
        return kind(
            dcc.Markdown(**filter_kwargs(opts, children=children, id=id)),
            component_property=component_property,
            label=label,
            location=location,
        )

    @classmethod
    def new_textarea(
        cls,
        value=None,
        label=Component.UNDEFINED,
        kind=Input,
        location=Component.UNDEFINED,
        component_property="value",
        id=None,
        opts=None,
    ):
        return kind(
            dcc.Textarea(**filter_kwargs(opts, value=value, id=id)),
            component_property=component_property,
            label=label,
            location=location,
        )

    @classmethod
    def new_button(
        cls,
        children,
        label=Component.UNDEFINED,
        kind=Input,
        location=Component.UNDEFINED,
        component_property="n_clicks",
        id=None,
        opts=None,
    ):
        return kind(
            html.Button(children=children, **filter_kwargs(opts, id=id)),
            component_property=component_property,
            label=label,
            location=location,
        )

    @classmethod
    def new_dropdown(
        cls,
        options,
        value=Component.UNDEFINED,
        clearable=False,
        label=Component.UNDEFINED,
        kind=Input,
        location=Component.UNDEFINED,
        component_property="value",
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
            location=location,
        )

    @classmethod
    def new_slider(
        cls,
        min,
        max,
        value=Component.UNDEFINED,
        step=None,
        tooltip=None,
        label=Component.UNDEFINED,
        kind=Input,
        location=Component.UNDEFINED,
        component_property="value",
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
            location=location,
        )

    @classmethod
    def new_range_slider(
        cls,
        min,
        max,
        value=Component.UNDEFINED,
        step=None,
        tooltip=None,
        label=Component.UNDEFINED,
        kind=Input,
        location=Component.UNDEFINED,
        component_property="value",
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
            value = [min, max]

        return kind(
            dcc.RangeSlider(
                min=min,
                max=max,
                **filter_kwargs(opts, tooltip=tooltip, step=step, value=value, id=id)
            ),
            component_property=component_property,
            label=label,
            location=location,
        )

    @classmethod
    def new_textbox(
        cls,
        value=None,
        label=Component.UNDEFINED,
        kind=Input,
        location=Component.UNDEFINED,
        component_property="value",
        id=None,
        opts=None,
    ):
        return kind(
            dcc.Input(value=value, **filter_kwargs(opts, id=id)),
            component_property=component_property,
            label=label,
            location=location,
        )

    @classmethod
    def new_checklist(
        cls,
        options,
        value=None,
        label=Component.UNDEFINED,
        kind=Input,
        location=Component.UNDEFINED,
        component_property="value",
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
            location=location,
        )

    @classmethod
    def new_graph(
        cls,
        figure=None,
        config=None,
        label=Component.UNDEFINED,
        kind=Output,
        location=Component.UNDEFINED,
        component_property="figure",
        id=None,
        opts=None,
    ):
        return kind(
            cls._graph_class()(
                **filter_kwargs(opts, figure=figure, config=config, id=id)
            ),
            component_property=component_property,
            label=label,
            location=location,
        )

    @classmethod
    def new_date_picker_single(
        cls,
        date=None,
        label=Component.UNDEFINED,
        kind=Input,
        location=Component.UNDEFINED,
        component_property="date",
        id=None,
        opts=None,
    ):
        if isinstance(date, datetime.date):
            date = date.isoformat()

        return kind(
            dcc.DatePickerSingle(date=date, **filter_kwargs(opts, id=id)),
            component_property=component_property,
            label=label,
            location=location,
        )

    @classmethod
    def new_date_picker_range(
        cls,
        start_date=None,
        end_date=None,
        label=Component.UNDEFINED,
        kind=Input,
        location=Component.UNDEFINED,
        component_property=("start_date", "end_date"),
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
            location=location,
        )

    # Methods specifying default classes for various components
    @classmethod
    def _graph_class(cls):
        return dcc.Graph

    @classmethod
    def _datatable_class(cls):
        from dash_table import DataTable

        return DataTable
