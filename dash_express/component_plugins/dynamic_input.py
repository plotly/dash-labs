from dash_express import build_id
from dash_express.dependency import Output, Input
from .base import ComponentPlugin


class DynamicInputPlugin(ComponentPlugin):
    """
    Support dynamic labels and checkbox to disable input component
    """

    def __init__(self, input_dependency, template):
        self.input_dependency = input_dependency
        self.label_string = self.input_dependency.label
        self.label_id = build_id("label")
        self.label_prop = template._label_value_prop

        self.input_dependency.label = self.label_string
        self.input_dependency.label_id = self.label_id

    @property
    def inputs(self):
        return self.input_dependency

    @property
    def output(self):
        return dict(
            label_value=Output(self.label_id, self.label_prop),
        )

    def build(self, inputs_value):
        return dict(label_value=self._format_label(inputs_value))

    def _format_label(self, value):
        return self.label_string.format(value)

    def get_value(self, inputs_value):
        return inputs_value["value"]
