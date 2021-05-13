from collections import OrderedDict
from dash_labs.dependency import Output, Input
from dash_labs.templates.base import BaseTemplate
import dash_html_components as html
from dash_labs.util import filter_kwargs, build_id


def import_ddk():
    try:
        import dash_design_kit as ddk
    except ImportError:
        raise ImportError(
            """
Module not found: dash_design_kit.
To use templates powered by Dash Enterprise Design Kit, please ensure that you 
have dash_design_kit installed in your app's Python environment. You can refer 
to your organization's Dash Enterprise documentation for instructions on how 
to do this.  If your organization is not yet a Dash Enterprise customer, 
please visit https://plotly.com/get-demo/ to find out more!"""
        )

    return ddk


class BaseDDKTemplate(BaseTemplate):
    """
    Base class for templates based on Dash Design Kit
    """

    _label_value_prop = "label"

    def __init__(
        self,
        app,
    ):
        """
        :param app: dash.Dash app instance
        """
        super(BaseDDKTemplate, self).__init__(app)

    @classmethod
    def build_labeled_component(cls, component, label, label_id=None, role=None):
        ddk = import_ddk()

        # Subclass could use bootstrap or ddk
        if not label_id:
            label_id = build_id("label")

        container = ddk.ControlItem(id=label_id, label=label, children=component)
        label_component = container
        label_property = "label"

        return container, "children", label_component, label_property

    @classmethod
    def build_containered_component(cls, component, role=None):
        ddk = import_ddk()

        # Subclass could use bootstrap or ddk
        container_id = build_id("container")
        container = ddk.ControlItem(id=container_id, children=component)

        return container, "children"

    @classmethod
    def _graph_class(cls):
        ddk = import_ddk()

        return ddk.Graph

    @classmethod
    def _datatable_class(cls):
        from dash_table import DataTable

        return DataTable


class DdkCard(BaseDDKTemplate):
    def __init__(self, app, title=None, width=None, height=None, **kwargs):
        """
        Template that places all components in a single card

        :param app: dash.Dash app instance
        :param title: Card title
        :param width: Proportional width of the card (out of 100)
        :param height: Height of the card (in pixels)
        """
        self.title = title
        self.width = width
        self.height = height
        super().__init__(app)

    def _perform_layout(self):
        ddk = import_ddk()

        # No callbacks here. Must be constant or idempotent
        card_children = []
        if self.title:
            card_children.append(ddk.CardHeader(title=self.title))

        card_children.append(
            html.Div(
                style={"padding": 20}, children=html.Div(self.get_containers("output"))
            )
        )
        card_children.append(html.Hr(style={"width": "100%", "margin": "auto"}))
        card_children.extend(self.get_containers("input"))

        layout = ddk.ControlCard(
            children=card_children,
            **filter_kwargs(width=self.width),
        )

        return layout


class DdkRow(BaseDDKTemplate):
    def __init__(self, app, title=None, input_width=30):
        """
        Template that places inputs and outputs in separate cards, arranged in a row

        :param app: dash.Dash app instance
        :param title: Input card title
        :param input_width: Input width proportion (out of 100)
        """
        self.title = title
        self.input_width = input_width
        super().__init__(app)

    def _perform_layout(self):
        ddk = import_ddk()

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
    def __init__(self, app, title=None, sidebar_width=300):
        """
        Template that includes a title bar, places inputs in a sidebar, and outputs in
        the main area of the app.

        :param app: dash.Dash app instance
        :param title: Title bar title string
        :param sidebar_width: Sidebar width in pixels or as a css string
        """
        self.title = title
        self.sidebar_width = sidebar_width
        super().__init__(app)

    def _perform_layout(self):
        ddk = import_ddk()

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


class DdkSidebarTabs(BaseDDKTemplate):
    def __init__(self, app, tab_roles, title=None, sidebar_width=300, **kwargs):
        """
        Template that includes a title bar, places inputs in a sidebar, and outputs in
        a set of tabs

        :param app: dash.Dash app instance
        :param tab_roles: List or dict of strings where each string specifies the name
            of the role corresponding to a single tab. If a list, the role name is
            also be used as the title of the corresponding tab. If a dict, the keys
            become the roles and the values become the tab labels
        :param title: Title bar title string
        :param sidebar_width: Sidebar width in pixels or as a css string
        """
        import dash_core_components as dcc

        self.title = title
        self.sidebar_width = sidebar_width
        if isinstance(tab_roles, (list, tuple)):
            self.tab_roles = OrderedDict([(role, role) for role in tab_roles])
        else:
            self.tab_roles = OrderedDict(tab_roles)

        self._valid_roles = ["input", "output"] + list(self.tab_roles.keys())
        self._tabs = dcc.Tabs(id=build_id("tabs"), value=self._valid_roles[2])

        super().__init__(app)

    def _perform_layout(self):
        ddk = import_ddk()
        import dash_core_components as dcc

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

        self._tabs.children = [
            dcc.Tab(
                value=role,
                label=title,
                children=ddk.ControlCard(list(reversed(self.get_containers(role)))),
            )
            for role, title in self.tab_roles.items()
        ]

        sidebar_companion = ddk.SidebarCompanion(self._tabs)
        children.append(sidebar_companion)

        return children

    def tab_input(self, kind=Input):
        """
        Dependency object that can be used to input the active tab
        :param kind: The dependency kind to return. One of dl.Input (default) or
            dl.State.
        :return: Dependency object referencing the active tab
        """
        return kind(self._tabs.id, "value")
