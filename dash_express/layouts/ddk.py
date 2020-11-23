from dash_express.layouts.component_layout import ComponentLayout
import dash_html_components as html

from dash_express.layouts.util import filter_kwargs


class BaseDDKLayout(ComponentLayout):
    @property
    def layout(self):
        import dash_design_kit as ddk

        # No callbacks here. Must be constant or idempotent
        card_children = []
        if self.title:
            card_children.append(ddk.CardHeader(title=self.title))

        card_children.append(html.Div(
            style={"padding": 20},
            children=html.Div(self._components['output'])
        ))
        card_children.append(html.Hr(
            style={"width": "100%", "margin": "auto"}
        ))
        card_children.extend(self._components['input'])

        layout = ddk.ControlCard(
            width=self.width,
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


class DdkCardLayout(ComponentLayout):
    def __init__(self, app, width=None, height=None, **kwargs):
        super().__init__(app, **kwargs)
        self.width = width
        self.height = height

    @property
    def layout(self):
        import dash_design_kit as ddk

        # No callbacks here. Must be constant or idempotent
        card_children = []
        if self.title:
            card_children.append(ddk.CardHeader(title=self.title))

        card_children.append(html.Div(
            style={"padding": 20},
            children=html.Div(self._components['output'])
        ))
        card_children.append(html.Hr(
            style={"width": "100%", "margin": "auto"}
        ))
        card_children.extend(self._components['input'])

        layout = ddk.ControlCard(
            children=card_children,
            **filter_kwargs(width=self.width),
        )

        return layout


class DdkRowLayout(ComponentLayout):
    def __init__(self, app, input_width=None, **kwargs):
        super().__init__(app, **kwargs)
        self.input_width = input_width

    @property
    def layout(self):
        import dash_design_kit as ddk

        # Input card
        input_card = ddk.ControlCard(
            children=self._components['input'],
            **filter_kwargs(width=self.input_width),
        )

        output_card_children = []
        if self.title is not None:
            output_card_children.append(ddk.CardHeader(title=self.title))
        output_card_children.extend(self._components['output'])

        output_card = ddk.Card(children=output_card_children)

        layout = ddk.Row([
            input_card, output_card
        ])

        return layout


class DdkSidebarLayout(ComponentLayout):
    def __init__(self, app, sidebar_width="300px", **kwargs):
        super().__init__(app, **kwargs)
        self.sidebar_width = sidebar_width

    @property
    def layout(self):
        import dash_design_kit as ddk

        children = []

        if self.title is not None:
            children.append(ddk.Header([ddk.Title(self.title)]))

        # Input card
        sidebar_children = []
        sidebar_children.append(ddk.ControlCard(
            children=self._components['input'],
        ))

        sidebar = ddk.Sidebar(
            foldable=True,
            children=sidebar_children,
            style={'minWidth': self.sidebar_width if self.sidebar_width else 'auto'}
        )
        children.append(sidebar)

        output_card_children = []
        if self.title is not None:
            output_card_children.append(ddk.CardHeader(title=self.title))
        output_card_children.extend(self._components['output'])

        output_card = ddk.Card(children=output_card_children)

        sidebar_companion = ddk.SidebarCompanion(output_card)
        children.append(sidebar_companion)

        return children
