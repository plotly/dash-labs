from dash_labs.grouping import flatten_grouping
from dash_labs.templates import FlatDiv


class ComponentPlugin:
    """
    Base class for component plugins
    """

    def __init__(self, args, output, template=None):
        """
        Superclass constructor that should be called by subclass constructors

        :param args: Grouping of dependency objects that specify the inputs required
            by the component plugin. If the plugin does not require inputs, this should
            be set to an empty tuple.
        :param output: Grouping of dependency objects that specify the outputs produced
            by the component plugin.
        :param template: Template for use by template. Defaults to FlatDiv.
        """
        self._args = args
        self._output = output

        if template is None:
            template = FlatDiv(None)
        self.template = template

    def get_output_values(self, args_value):
        """
        Method that produces a grouping of the plugin's output values, which correspond
        to the dependency grouping returned by the args property

        :param args_value: grouping of values corresponding to the dependency
            grouping returned by the args property.
        :return: grouping of values corresponding to the dependency grouping returned
            by the output property
        """
        raise NotImplementedError

    @property
    def args(self):
        """
        :return: Grouping of Input/State dependency objects for the inputs required by
            the plugin's get_output_values method
        """
        return self._args

    @property
    def output(self):
        """
        :return: Grouping of Output dependency objects for the callback output values
            produced by the plugin's get_output_values method
        """
        return self._output

    def install_callback(self, app):
        """
        Convenience method to install the minimal required callback definition to
        use the plugin. This is useful for cases where the plugin doesn't need to
        integrate with any other components.

        :param app: dash.Dash app instance
        """

        @app.callback(
            args=[self.args],
            output=[self.output],
            template=self.template,
        )
        def callback(plugin_inputs):
            return [self.get_output_values(plugin_inputs)]

    @property
    def args_components(self):
        """
        :return: list of the components corresponding to the plugin's args dependencies
        """
        return [
            self.template.build_argument_components(
                c.component_id, label=c.label, label_id=c.label_id
            ).container_component
            for c in flatten_grouping(self.args)
            if c.has_component
        ]

    @property
    def output_components(self):
        """
        :return: list of the components corresponding to the plugin's output
            dependencies
        """
        return [
            self.template.build_argument_components(
                c.component_id, label=c.label, label_id=c.label_id
            ).container_component
            for c in flatten_grouping(self.output)
            if c.has_component
        ]

    @property
    def container(self):
        """
        :return: Collection of all arg and output components, stored in the default
            component container for the current template (typically an html.Div)
        """
        return self.template.default_output(
            children=self.args_components + self.output_components
        ).component_id
