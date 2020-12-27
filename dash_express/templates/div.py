from dash_express.templates.base import BaseTemplate
import dash_html_components as html


class FlatDiv(BaseTemplate):

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    def _perform_layout(self):
        # No callbacks here. Must be constant or idempotent
        children = []
        children.extend(self.input_containers)
        children.extend(self.output_containers)
        return html.Div(children=children)
