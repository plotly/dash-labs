import math

from dash_express.dependency import Output, Input
from dash_express.util import build_id, filter_kwargs
from .base import ComponentPlugin
from dash_express.templates import FlatDiv
import pandas as pd
from dash_table import DataTable


class DynamicInputPlugin(ComponentPlugin):
    """
    Support dynamic labels and checkbox to disable input component
    """

    def __init__(self, input_dependency, template):
        self.input_dependency = input_dependency
        self.label_string = self.input_dependency.label

        container_component, container_props, label, label_props = \
            template.build_labeled_component(
                self.input_dependency.component, initial_value=self.label_string
            )

        self.container_input = Input(container_component, container_props, label=None)
        self.label_input = Input(label, label_props)

    @property
    def inputs(self):
        return dict(
            component=self.container_input,
            value=self.input_dependency.dependencies,
        )

    @property
    def output(self):
        return dict(
            label_value=Output(self.label_input.id, self.label_input.component_property),
        )

    def build(self, inputs_value):
        value = inputs_value["value"]
        return dict(label_value=self.label_string.format(value))


    def get_value(self, inputs_value):
        return inputs_value["value"]
