from dash_express.templates.base import BaseTemplate
import dash_html_components as html


class FlatDiv(BaseTemplate):
    def __init__(self):
        super().__init__()

    def _perform_layout(self):
        # No callbacks here. Must be constant or idempotent
        children = []
        children.extend(self.get_containers("input"))
        children.extend(self.get_containers("output"))
        return html.Div(children=children)
