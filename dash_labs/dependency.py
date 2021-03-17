from dash.dependencies import (
    Input as Input_dash,
    Output as Output_dash,
    State as State_dash,
)
from dash.development.base_component import Component

from dash_labs import build_id
from dash_labs.grouping import make_grouping_by_index, flatten_grouping, map_grouping

"""
Module containing DashLabs versions of the standard Input/State/Output dash
dependencies. These versions support the use of full components in place of component
ids, and they support specifying property groupings in place of scalar properties.
"""


class DashLabsDependency:

    dependency_class = None

    def __init__(
        self,
        component_id,
        component_property="value",
        label=Component.UNDEFINED,
        role=Component.UNDEFINED,
        label_id=None,
    ):
        """
        :param component_id: Component id or component instance
        :param component_property: Grouping of component properties
        :param label: Template label for component
            (ignored if component_id is not a component)
        :param role: Template role for component
            (ignored if component_id is not a component)
        :param label_id: Custom id to use for template label
            (ignored if component_id is not a component or label is not defined)
        """
        self.set_component_and_props(component_id, component_property)
        self.label = label
        self.label_id = label_id
        self.role = role

    @property
    def id(self):
        """
        :return: Component's id if component_id is a component, otherwise component_id
        """
        if isinstance(self.component_id, (str, dict)):
            return self.component_id
        else:
            return self.component_id.id

    @property
    def has_component(self):
        """
        :return: Trued if component_id is a component instance, False otherwise
        """
        return isinstance(self.component_id, Component)

    def extract_component(self):
        """
        Extract the store component from dependency and construct dependency that
        references component by id

        :return: (dependency, component) tuple
        """
        if not self.has_component:
            raise ValueError(
                "extract_component only valid for dependency storing a component instance"
            )
        component = self.component_id
        dependency = type(self)(self.id, self.component_property)
        return component, dependency

    def set_component_and_props(self, component_id, component_property):
        """
        Set both component_id and component_property attributes

        :param component_id: New component_id or component instance
        :param component_property:  New component property grouping
        """
        if isinstance(component_id, Component):
            _validate_prop_grouping(component_id, component_property)
            self.component_id = component_id
            self.component_property = component_property

            if getattr(self.component_id, "id", None) is None:
                self.component_id.id = build_id()
        else:
            if not isinstance(component_id, (str, dict)):
                raise ValueError("Invalid component_id value: {}".format(component_id))
            self.component_id = component_id
            self.component_property = component_property

    def dependencies(self, labs=False):
        """
        :param labs: If True, return dash-labs dependency objects
            if False (default), return dash.dependency objects
        :return: Grouping of dash.dependency objects with structure matching the
            grouping structore of the component_property attribute
        """
        if labs:
            return self._make_dependency_grouping(self.__class__)
        else:
            return self._make_dependency_grouping(self.dependency_class)

    def flat_dependencies(self, labs=False):
        """
        :param labs: If True, return dash-labs dependency objects
            if False (default), return dash.dependency objects
        :return: Flat list of dash.dependency objects with length matching the number
            of scalar properties in the component_property grouping
        """
        if labs:
            return self._make_flat_dependencies(self.__class__)
        else:
            return self._make_flat_dependencies(self.dependency_class)

    @property
    def flat_props(self):
        """
        :return: Flat list of properties in component_property grouping
        """
        return flatten_grouping(self.component_property)

    def _make_flat_dependencies(self, dependency):
        return [dependency(self.id, prop) for prop in self.flat_props]

    def _make_dependency_grouping(self, dependency):
        return make_grouping_by_index(
            self.component_property, self._make_flat_dependencies(dependency)
        )

    def property_value(self):
        """
        :return: Return a grouping of component property values corresponding to the
            component_property grouping
        """
        if not self.has_component:
            raise ValueError(
                "property_value only valid for dependency storing a component instance"
            )
        return map_grouping(
            lambda p: getattr(self.component_id, p, None), self.component_property
        )

    def __str__(self):
        return (
            f"{self.__class__.__name__}(\n"
            f"    component_id={repr(self.component_id)},\n"
            f"    component_property={repr(self.component_property)}\n"
            f")"
        )

    def __repr__(self):
        return str(self)


class Input(DashLabsDependency):
    dependency_class = Input_dash


class State(DashLabsDependency):
    dependency_class = State_dash


class Output(DashLabsDependency):
    dependency_class = Output_dash


def _validate_prop_grouping(component, props):
    for prop in flatten_grouping(props):
        _validate_prop_name(component, prop)


def _validate_prop_name(component, prop_name):
    if (
        isinstance(prop_name, str)
        and prop_name.isidentifier()
        and prop_name in component._prop_names
    ):
        pass
    else:
        raise ValueError(
            "Invalid property {prop} received for component of type {typ}\n".format(
                prop=repr(prop_name), typ=type(component)
            )
        )
