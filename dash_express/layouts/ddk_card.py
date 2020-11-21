from dash_express.component_layout import ComponentLayout
import dash_html_components as html


class CardLayoutDDK(ComponentLayout):
    @property
    def layout(self):
        import dash_design_kit as ddk

        # No callbacks here. Must be constant or idempotent
        card_children = []
        if self.config.get("title", None):
            card_children.append(ddk.CardHeader(title=self.config["title"]))

        card_children.append(html.Div(
            style={"padding": 20},
            children=html.Div(self._components['output'])
        ))
        card_children.append(html.Hr(
            style={"width": "100%", "margin": "auto"}
        ))
        card_children.extend(self._components['input'])

        layout = ddk.ControlCard(
            width=self.config.get("width", 500),
            children=card_children
        )

        return layout

    def build_labeled_input(self, component, label_id, initial_value):
        import dash_design_kit as ddk

        # Subclass could use bootstrap or ddk
        layout_component = ddk.ControlItem(
            id=label_id, label=initial_value, children=component
        )
        return layout_component, "label"


ComponentLayout.register_component_layout("ddk_card", CardLayoutDDK)
