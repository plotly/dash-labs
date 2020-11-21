from dash_express.component_layout import ComponentLayout
import dash_html_components as html


class CardLayoutDcc(ComponentLayout):

    @property
    def layout(self):
        # No callbacks here. Must be constant or idempotent
        children = []
        if self.config.get("title", None):
            children.append(html.H2(self.config["title"]))
        children.append(html.Div(self._components['output']))
        children.append(html.Hr())
        children.append(html.Div(self._components['input']))
        layout = html.Div(
            style={
                "width": self.config.get("width", "500px"),
                "border": "2px solid lightgray",
                "padding": 10,
                "border-radius": "12px"},
            children=html.Div(children=children)
        )
        return layout


ComponentLayout.register_component_layout("dcc_card", CardLayoutDcc)
