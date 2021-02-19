from dash.dependencies import (
    Input as Input_dash, Output as Output_dash, State as State_dash
)
from dash.development.base_component import Component

from dash_express import build_id
from grouping import make_grouping_by_position, flatten_grouping


class DashExpressDependency:  # pylint: disable=too-few-public-methods

    dependency_class = None

    def __init__(
            self, component_id, component_property="value",
            label=Component.UNDEFINED, role=Component.UNDEFINED
    ):
        self.set_component_and_props(component_id, component_property)
        self.label = label
        self.role = role

    @property
    def id(self):
        if isinstance(self.component, (str, dict)):
            return self.component
        else:
            return self.component.id

    def set_component_and_props(self, component_id, component_property):
        if isinstance(component_id, Component):
            _validate_prop_grouping(component_id, component_property)
            self.component = component_id
            self.component_property = component_property

            if getattr(self.component, "id", None) is None:
                self.component.id = build_id()
        else:
            self.component = component_id
            self.component_property = component_property

    @property
    def dependencies(self):
        return self._make_dependency_grouping(self.dependency_class)

    @property
    def flat_dependencies(self):
        return self._make_flat_dependencies(self.dependency_class)

    @property
    def flat_props(self):
        return flatten_grouping(self.component_property)

    def _make_flat_dependencies(self, dependency):
        return [dependency(self.id, prop) for prop in self.flat_props]

    def _make_dependency_grouping(self, dependency):
        return make_grouping_by_position(
            self.component_property, self._make_flat_dependencies(dependency)
        )


class Input(DashExpressDependency):
    dependency_class = Input_dash


class State(DashExpressDependency):
    dependency_class = State_dash


class Output(DashExpressDependency):
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
