from dash_labs.templates.base import BaseTemplate
import dash_html_components as html


class FlatDiv(BaseTemplate):
    _valid_locations = ("main",)

    # Default template location for `Input` and 'State' dependencies
    _default_input_location = "main"

    # Default template location for `Output` dependencies
    _default_output_location = "main"

    def __init__(self, app):
        """
        Trivial template that groups all input containers in a single flat Div

        :param app: dash.Dash app instance
        """
        super().__init__(app)

    def _perform_layout(self):
        children = []
        children.extend(self.get_containers("main"))
        return html.Div(children=children)
