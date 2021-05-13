from dash_labs.templates.base import BaseTemplate
import dash_html_components as html


class FlatDiv(BaseTemplate):
    def __init__(self, app):
        """
        Trivial template that groups all input containers in a single flat Div,
        inputs followed by outputs

        :param app: dash.Dash app instance
        """
        super().__init__(app)

    def _perform_layout(self):
        children = []
        children.extend(self.get_containers("input"))
        children.extend(self.get_containers("output"))
        return html.Div(children=children)
