from dash_labs import build_id, templates
from dash_labs.dependency import Output, Input
from dash_labs.grouping import flatten_grouping
from .base import ComponentPlugin


class DynamicInputPlugin(ComponentPlugin):
    """
    Support dynamic labels and checkbox to disable input component
    """

    def __init__(self, input_dependency, template=None):
        if template is None:
            template = templates.FlatDiv()

        self.input_dependency = input_dependency
        self.label_string = self.input_dependency.label
        self.label_id = build_id("label")
        self.label_prop = template._label_value_prop

        self.input_dependency.label = self.label_string
        self.input_dependency.label_id = self.label_id

        # Init args and output
        self._args = dict(value=self.input_dependency)
        self._output = dict(
            label_value=Output(self.label_id, self.label_prop),
        )

        # Create custom _args_component that holds the labeled component
        self._args_component = template.build_labeled_component(
            self.input_dependency.component_id, self.label_string, self.label_id
        )[0]

    def get_value(self, inputs_value):
        return inputs_value["value"]

    def get_output_values(self, inputs_value):
        return dict(label_value=self._format_label(self.get_value(inputs_value)))

    def install_callback(self, app):
        if not flatten_grouping(self.args):
            # No inputs, nothing to do
            return

        @app.callback(
            args=[self.args],
            output=[self.output],
        )
        def callback(plugin_inputs):
            return [self.get_output_values(plugin_inputs)]

    @property
    def args_components(self):
        return [self._args_component]

    def _format_label(self, value):
        return self.label_string.format(value)
