from dash.dependencies import (
    Input as Input_dash, Output as Output_dash, State as State_dash
)
from dash.development.base_component import Component

from dash_express import build_id
from dash_express.grouping import make_grouping_by_position, flatten_grouping, map_grouping


class DashExpressDependency:  # pylint: disable=too-few-public-methods

    dependency_class = None

    def __init__(
            self, component_id, component_property="value",
            label=Component.UNDEFINED, role=Component.UNDEFINED, containered=True,
            label_id=None,
    ):
        self.set_component_and_props(component_id, component_property)
        self.label = label
        self.label_id = label_id
        self.role = role
        self.containered = containered

    @property
    def id(self):
        if isinstance(self.component_id, (str, dict)):
            return self.component_id
        else:
            return self.component_id.id

    @property
    def has_component(self):
        return isinstance(self.component_id, Component)

    def set_component_and_props(self, component_id, component_property):
        if isinstance(component_id, Component):
            _validate_prop_grouping(component_id, component_property)
            self.component_id = component_id
            self.component_property = component_property

            if getattr(self.component_id, "id", None) is None:
                self.component_id.id = build_id()
        else:
            if not isinstance(component_id, (str, dict)):
                raise ValueError("Invalid component_id value: {}".format(component_id))
            if not isinstance(component_property, str):
                raise ValueError(
                    "Dependencies that don't reference a component must specify single "
                    "property as a string"
                )
            self.component_id = component_id
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

    def property_value(self):
        assert self.has_component
        return map_grouping(
            lambda p: getattr(self.component_id, p, None), self.component_property
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
