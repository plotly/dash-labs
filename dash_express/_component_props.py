from dash.dependencies import Input, State, Output

from .grouping import (
    flatten_grouping, make_grouping_by_attr, make_grouping_by_position, grouping_len
)
from .util import build_id
from dash.development.base_component import Component
from dataclasses import dataclass
from typing import Union, Tuple, Dict


class ComponentPropsAccessor:
    def __init__(self, component):
        assert isinstance(component, Component)
        self._component = component

    def __getitem__(self, item):
        return ComponentProps(self._component, item)


# install accessor
def get_component_props_accessor(self):
    return ComponentPropsAccessor(self)


setattr(Component, "props", property(get_component_props_accessor))


# # install value-based component equality
# def component_eq(self, other):
#     from plotly.utils import PlotlyJSONEncoder
#     import json
#     return type(self) is type(other) and (
#         json.dumps(self, cls=PlotlyJSONEncoder, sort_keys=True) ==
#         json.dumps(other, cls=PlotlyJSONEncoder, sort_keys=True)
#     )
#
# setattr(Component, "__eq__", component_eq)


@dataclass(frozen=True)
class ComponentProps:
    component: Component
    props: Union[str, Tuple, Dict]

    def __post_init__(self):
        # Validation properties in props
        _validate_prop_grouping(self.component, self.props)

        # Make sure component has id
        if getattr(self.component, "id", None) is None:
            self.component.id = build_id()

    @property
    def id(self):
        return self.component.id

    @property
    def flat_props(self):
        return flatten_grouping(self.props)

    @property
    def props_len(self):
        return grouping_len(self.props)

    @property
    def value(self):
        return make_grouping_by_attr(self.props, self.component, default=None)

    @property
    def flat_value(self):
        return flatten_grouping(self.value)

    @property
    def input(self):
        return self._make_dependency_grouping(Input)

    @property
    def flat_input(self):
        return self._make_flat_dependencies(Input)

    @property
    def state(self):
        return self._make_dependency_grouping(State)

    @property
    def flat_state(self):
        return self._make_flat_dependencies(State)

    @property
    def output(self):
        return self._make_dependency_grouping(Output)

    @property
    def flat_output(self):
        return self._make_flat_dependencies(Output)

    def _make_flat_dependencies(self, dependency):
        return [dependency(self.component.id, prop) for prop in self.flat_props]

    def _make_dependency_grouping(self, dependency):
        return make_grouping_by_position(
            self.props, self._make_flat_dependencies(dependency)
        )


def _raise_for_invalid_props(component, props):
    raise ValueError(
        "Invalid component property or property collection {item} "
        "for component of type {typ}".format(item=repr(props), typ=type(component))
    )


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


def _validate_prop_grouping(component, props):
    for prop in flatten_grouping(props):
        _validate_prop_name(component, prop)
