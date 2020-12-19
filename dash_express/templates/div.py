from dash_express.templates.base import BaseTemplateInstance
import dash_html_components as html


class FlatDiv(BaseTemplateInstance):

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    def _perform_layout(self):
        # No callbacks here. Must be constant or idempotent
        children = []
        children.extend(self._components['input'])
        children.extend(self._components['output'])
        return html.Div(children=children)
