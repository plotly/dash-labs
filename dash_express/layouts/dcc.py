from dash_express.layouts.component_layout import ComponentLayout
import dash_html_components as html


class DccCardLayout(ComponentLayout):

    def __init__(self, app=None, width=None, **kwargs):
        super().__init__(app=app, **kwargs)
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
