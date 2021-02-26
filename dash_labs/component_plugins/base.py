from grouping import flatten_grouping
import dash_html_components as html


class ComponentPlugin:

    @property
    def args(self):
        if not hasattr(self, "_args"):
            raise NotImplementedError
        return self._args

    @property
    def output(self):
        if not hasattr(self, "_output"):
            raise NotImplementedError
        return self._output

    def get_output_values(self, inputs_value):
        raise NotImplementedError

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
        return [
            c.component_id for c in flatten_grouping(self.args) if c.has_component
        ]

    @property
    def output_components(self):
        return [
            c.component_id for c in flatten_grouping(self.output) if c.has_component
        ]

    @property
    def components_div(self):
        return html.Div(children=self.args_components + self.output_components)
