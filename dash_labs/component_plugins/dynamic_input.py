from dash_labs import build_id, templates
from dash_labs.dependency import Output
from .base import ComponentPlugin


class DynamicLabelPlugin(ComponentPlugin):
    """
    Plugin that supports formatting a component's template label with the current
    component value
    """

    def __init__(self, input_dependency, template=None):
        if template is None:
            template = templates.FlatDiv(None)

        self.input_dependency = input_dependency
        self.format_string = self.input_dependency.label
        self.label_string = self.format_string.format(input_dependency.property_value())
        self.label_id = build_id("label")
        self.label_prop = template._label_value_prop

        self.input_dependency.label = self.label_string
        self.input_dependency.label_id = self.label_id

        # Init args and output
        args = dict(value=self.input_dependency)
        output = dict(
            label_value=Output(self.label_id, self.label_prop),
        )

        super(DynamicLabelPlugin, self).__init__(args=args, output=output)

    def get_value(self, args_value):
        """
        :param args_value: grouping of values corresponding to the dependency
            grouping returned by the args property
        :return: The value of the wrapped component
        """
        return args_value["value"]

    def get_output_values(self, args_value):
        return dict(label_value=self._format_label(self.get_value(args_value)))

    def _format_label(self, value):
        return self.format_string.format(value)
