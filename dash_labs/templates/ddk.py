from dash.development.base_component import Component

from dash_labs.dependency import Output
from dash_labs.templates.base import BaseTemplate
import dash_html_components as html

from dash_labs.util import filter_kwargs, build_id


class BaseDDKTemplate(BaseTemplate):
    _label_value_prop = "label"

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
        super(BaseDDKTemplate, self).__init__()
        self.theme = theme
        self.show_editor = show_editor
        self.theme_dev_tools = theme_dev_tools
        self.embedded = embedded
        self.show_undo_redo = show_undo_redo
        self.use_mobile_viewport = use_mobile_viewport

    @classmethod
    def build_labeled_component(cls, component, label, label_id=None, role=None):
        import dash_design_kit as ddk

        # Subclass could use bootstrap or ddk
        if not label_id:
            label_id = build_id("label")

        container = ddk.ControlItem(
            id=label_id, label=label, children=component
        )
        label_component = container
        label_property = "label"

        return container, "children", label_component, label_property

    @classmethod
    def build_containered_component(cls, component, role=None):
        import dash_design_kit as ddk

        # Subclass could use bootstrap or ddk
        container_id = build_id("container")
        container = ddk.ControlItem(id=container_id, children=component)

        return container, "children"

    @classmethod
    def _graph_class(cls):
        import dash_design_kit as ddk
        return ddk.Graph

    @classmethod
    def _datatable_class(cls):
        from dash_table import DataTable
        return DataTable

    def _wrap_full_layout(self, layout):
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
            ),
        )


class DdkCard(BaseDDKTemplate):
    def __init__(self, title=None, width=None, height=None, **kwargs):
        super().__init__(**kwargs)
        self.title = title
        self.width = width
        self.height = height

    def _perform_layout(self):
        import dash_design_kit as ddk

        # No callbacks here. Must be constant or idempotent
        card_children = []
        if self.title:
            card_children.append(ddk.CardHeader(title=self.title))

        card_children.append(
            html.Div(style={"padding": 20}, children=html.Div(self.get_containers("output")))
        )
        card_children.append(html.Hr(style={"width": "100%", "margin": "auto"}))
        card_children.extend(self.get_containers("input"))

        layout = ddk.ControlCard(
            children=card_children,
            **filter_kwargs(width=self.width),
        )

        return layout


class DdkRow(BaseDDKTemplate):
    def __init__(self, title=None, input_width=30, **kwargs):
        super().__init__(**kwargs)
        self.title = title
        self.input_width = input_width

    def _perform_layout(self):
        import dash_design_kit as ddk

        # Input card
        input_card = ddk.ControlCard(
            children=self.get_containers("input"),
            width=self.input_width,
        )

        output_card_children = []
        if self.title is not None:
            output_card_children.append(ddk.CardHeader(title=self.title))
        output_card_children.extend(self.get_containers("output"))

        output_card = ddk.ControlCard(
            children=output_card_children,
            width=100 - self.input_width,
        )

        row_children = [input_card, output_card]
        layout = ddk.Row(row_children)

        return layout


class DdkSidebar(BaseDDKTemplate):
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
        sidebar_children.append(
            ddk.ControlCard(
                children=self.get_containers("input"),
            )
        )

        sidebar = ddk.Sidebar(
            foldable=True,
            children=sidebar_children,
            style={"minWidth": self.sidebar_width if self.sidebar_width else "auto"},
        )
        children.append(sidebar)

        output_card_children = []
        output_card_children.extend(self.get_containers("output"))

        output_card = ddk.ControlCard(output_card_children)

        sidebar_companion = ddk.SidebarCompanion(output_card)
        children.append(sidebar_companion)

        return children
