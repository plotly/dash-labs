from dash_express.templates.base import BaseTemplate, BaseTemplateBuilder
import dash_html_components as html

from dash_express.templates.util import filter_kwargs


class BaseDDKTemplate(BaseTemplate):
    def __init__(
            self,
            theme=None,
            show_editor=None,
            theme_dev_tools=None,
            embedded=None,
            show_undo_redo=None,
            use_mobile_viewport=None,
            **kwargs,
    ):
        super(BaseDDKTemplate, self).__init__(**kwargs)
        self.theme = theme
        self.show_editor = show_editor
        self.theme_dev_tools = theme_dev_tools
        self.embedded = embedded
        self.show_undo_redo = show_undo_redo
        self.use_mobile_viewport = use_mobile_viewport

    @classmethod
    def build_labeled_component(cls, component, label_id, initial_value):
        import dash_design_kit as ddk

        # Subclass could use bootstrap or ddk
        layout_component = ddk.ControlItem(
            id=label_id, label=initial_value, children=component
        )
        return layout_component, "label"

    @classmethod
    def build_graph(cls, figure, **kwargs):
        import dash_design_kit as ddk
        return ddk.Graph(figure=figure, **filter_kwargs(**kwargs))


class DdkCardTemplate(BaseDDKTemplate):
    def __init__(self, app=None, title=None, width=None, height=None, **kwargs):
        super().__init__(app=app, **kwargs)
        self.title = title
        self.width = width
        self.height = height

    def _perform_layout(self):
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


class DdkRowTemplate(BaseDDKTemplate):
    def __init__(self, app=None, title=None, input_width=30, **kwargs):
        super().__init__(app=app, **kwargs)
        self.title = title
        self.input_width = input_width

    def _perform_layout(self):
        import dash_design_kit as ddk

        # Input card
        input_card = ddk.ControlCard(
            children=self._components['input'],
            width=self.input_width,
            # **filter_kwargs(width=self.input_width),
        )

        output_card_children = []
        if self.title is not None:
            output_card_children.append(ddk.CardHeader(title=self.title))
        output_card_children.extend(self._components['output'])

        output_card = ddk.Card(
            children=output_card_children,
            width=100 - self.input_width,
            # width=80
        )

        row_children = [
            input_card, output_card
        ]
        layout = ddk.Row(row_children)

        return layout


class DdkSidebarTemplate(BaseDDKTemplate):
    def __init__(self, title=None, sidebar_width="300px", **kwargs):
        super().__init__(**kwargs)
        self.title = title
        self.sidebar_width = sidebar_width

    def _perform_layout(self):
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
        output_card_children.extend(self._components['output'])

        output_card = ddk.Card(children=output_card_children)

        sidebar_companion = ddk.SidebarCompanion(output_card)
        children.append(sidebar_companion)

        return children

    def _app_wrapper(self, layout):
        import dash_design_kit as ddk
        return ddk.App(
            children=layout,
            **filter_kwargs(
                theme=self.theme,
                show_editor=self.show_editor,
                theme_dev_tools=self.theme_dev_tools,
                embedded=self.embedded,
                show_undo_redo=self.show_undo_redo,
                use_mobile_viewport=self.use_mobile_viewport,
            )
        )


class BaseDdkTemplateBuilder(BaseTemplateBuilder):
    _label_value_prop = "label"


class DdkCard(BaseDdkTemplateBuilder):
    _template_cls = DdkCardTemplate

    def __init__(self, title=None, width=None, height=None, **kwargs):
        """
        TODO: User docstring here
        """
        super().__init__(
            title=title, width=width, height=height, **kwargs
        )


class DdkRow(BaseDdkTemplateBuilder):
    _template_cls = DdkRowTemplate

    def __init__(self, title=None, input_width=30, **kwargs):
        """
        TODO: User docstring here
        Also the common DDK options:
            theme=None,
            show_editor=None,
            theme_dev_tools=None,
            embedded=None,
            show_undo_redo=None,
            use_mobile_viewport=None,
        """
        super().__init__(
            title=title, input_width=input_width, **kwargs
        )


class DdkSidebar(BaseDdkTemplateBuilder):
    _template_cls = DdkSidebarTemplate

    def __init__(self, title=None, sidebar_width="300px", **kwargs):
        """
        TODO: User docstring here
        """
        super().__init__(
            title=title, sidebar_width=sidebar_width, **kwargs
        )
