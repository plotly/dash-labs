from dash_express.templates.base import BaseTemplateInstance, BaseTemplate
import dash_html_components as html


class DccCardTemplateInstance(BaseTemplateInstance):

    def __init__(self, title=None, width=None, **kwargs):
        super().__init__(**kwargs)
        self.title = title
        self.width = width

    def _perform_layout(self):
        # No callbacks here. Must be constant or idempotent
        children = []
        if self.title:
            children.append(html.H2(self.title))
        children.append(html.Div(self._components['output']))
        children.append(html.Hr())
        children.append(html.Div(self._components['input']))
        layout = html.Div(
            style={
                "width": self.width,
                "border": "1px solid lightgray",
                "padding": 10,
                "border-radius": "6px"},
            children=html.Div(children=children)
        )
        return layout


class DccCard(BaseTemplate):
    _template_instance_cls = DccCardTemplateInstance

    def __init__(self, title=None, width=None, **kwargs):
        super().__init__(
            title=title, width=width, **kwargs
        )
