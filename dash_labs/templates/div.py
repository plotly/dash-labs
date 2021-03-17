from dash_labs.templates.base import BaseTemplate
import dash_html_components as html


class FlatDiv(BaseTemplate):
    """
    Trivial template that returns all input containers in a single flat Div,
    inputs followed by outputs
    """

    def __init__(self):
        super().__init__()

    def _perform_layout(self):
        children = []
        children.extend(self.get_containers("input"))
        children.extend(self.get_containers("output"))
        return html.Div(children=children)
