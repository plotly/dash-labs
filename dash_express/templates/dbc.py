from dash_express.templates.base import BaseTemplate
import dash_html_components as html
from dash_express.util import filter_kwargs, build_id


class BaseDbcTemplate(BaseTemplate):
    # - Align sliders vertically with an outline that matches dropdowns/inputs
    # - Undo the negative margins that table rows pick up from bootstrap's own row
    #   CSS class. Otherwise, table expand in width outside of their container.
    _inline_css = """
            <style>
            .dcc-slider {
                padding: 12px 20px 12px 20px !important;
                border: 1px solid #ced4da;
                border-radius: .25rem;
             }
             
             .dash-spreadsheet .row {
                margin-left: 0;
                margin-right: 0;
             }
             
             .param-markdown > p {
                margin-bottom: 0.5rem;
             }
             .param-markdown > p:last-of-type {
                margin-bottom: 0;
             }
            </style>"""

    def __init__(self, theme=None, **kwargs):
        super().__init__()
        self.theme = theme

    # Methods designed to be overridden by subclasses
    @classmethod
    def Button(cls, children=None, id=None, **kwargs):
        import dash_bootstrap_components as dbc

        return dbc.Button(**filter_kwargs(children=children, id=id, **kwargs))

    @classmethod
    def Dropdown(cls, options, id=None, value=None, **kwargs):
        import dash_bootstrap_components as dbc

        if value is None:
            value = options[0]["value"]

        return dbc.Select(options=options, value=value, **filter_kwargs(id=id))

    @classmethod
    def Input(cls, value=None, id=None, **kwargs):
        import dash_bootstrap_components as dbc

        return dbc.Input(value=value, **filter_kwargs(id=id, **kwargs))

    @classmethod
    def Checkbox(cls, option, value=None, id=None, **kwargs):
        import dash_bootstrap_components as dbc

        if isinstance(option, str):
            option = {"label": option, "value": option}

        return dbc.Checklist(
            options=[option],
            value=value if value is not None else option["value"],
            **filter_kwargs(id=id, **kwargs),
        )

    @classmethod
    def build_optional_component(self, component, enabled=True):
        """ Should come before labeling """
        import dash_bootstrap_components as dbc

        checkbox_id = build_id(
            kind="disable-checkbox",
            name=str(component.id["name"]) + "-enabled",
        )
        checkbox = dbc.Checkbox(id=checkbox_id, checked=enabled)
        checkbox_property = "checked"

        container = dbc.InputGroup(
            [
                dbc.InputGroupAddon(checkbox, addon_type="prepend"),
                html.Div(style=dict(flex="auto"), children=component),
            ]
        )
        return container, "children", checkbox, checkbox_property

    @classmethod
    def build_labeled_component(cls, component, initial_value):
        import dash_bootstrap_components as dbc
        label_id = build_id("label")
        label = dbc.Label(
            id=label_id, children=[initial_value], style={"display": "block"}
        )
        container_id = build_id("container")
        container = dbc.FormGroup(id=container_id, children=[label, component])
        return container.props["children"], label.props["children"]


    @classmethod
    def build_containered_component(cls, component):
        import dash_bootstrap_components as dbc

        container_id = build_id("container")
        container = dbc.FormGroup(id=container_id, children=[component])
        return container.props["children"]

    def _configure_app(self, app):
        super()._configure_app(app)
        import dash_bootstrap_components as dbc

        # Check if there are any bootstrap css themes already added
        add_theme = True
        for url in app.config.external_stylesheets:
            if "bootstrapcdn" in url:
                add_theme = False
                break
        if add_theme:
            if self.theme is None:
                app.config.external_stylesheets.append(dbc.themes.BOOTSTRAP)
            else:
                app.config.external_stylesheets.append(self.theme)



class DbcCard(BaseDbcTemplate):
    def __init__(
        self, title=None, full=True, columns=12, min_width=400, height=None, **kwargs
    ):
        super().__init__(**kwargs)
        self.title = title
        self.full = full
        self.columns = columns
        self.height = height
        self.min_width = min_width

    def _perform_layout(self):
        import dash_bootstrap_components as dbc

        # No callbacks here. Must be constant or idempotent
        card_children = []
        if self.title:
            card_children.append(dbc.CardHeader(self.title))

        card_body_children = []
        card_body_children.extend(self.get_containers("output"))
        card_body_children.append(html.Hr())
        card_body_children.extend(self.get_containers("input"))

        card_children.append(dbc.CardBody(children=card_body_children))

        card_style = {"padding": 0}
        if self.height is not None:
            card_style["height"] = self.height

        if self.min_width is not None:
            card_style["min-width"] = self.min_width

        class_name_kwarg = {}
        if self.columns is not None:
            class_name_kwarg["className"] = f"col-{int(self.columns)}"

        return dbc.Card(
            style=card_style,
            children=card_children,
            **class_name_kwarg,
        )


class DbcRow(BaseDbcTemplate):
    def __init__(
        self,
        title=None,
        row_height=None,
        input_cols=4,
        min_input_width="300px",
        **kwargs,
    ):
        super().__init__(**kwargs)
        self.title = title
        self.row_height = row_height
        self.input_cols = input_cols
        self.min_input_width = min_input_width

    def _perform_layout(self):
        import dash_bootstrap_components as dbc

        output_card_children = []
        if self.title:
            output_card_children.append(dbc.CardHeader(self.title))

        output_card_children.extend(self.get_containers("output"))

        input_card_style = {}
        if self.min_input_width is not None:
            input_card_style["min-width"] = self.min_input_width

        row_style = {}
        if self.row_height is not None:
            row_style["height"] = self.row_height

        class_name_kwarg = {}
        if self.input_cols is not None:
            class_name_kwarg["className"] = f"col-{int(self.input_cols)}"

        return dbc.Row(
            style=row_style,
            children=[
                dbc.Col(
                    children=dbc.Card(children=self.get_containers("input"), body=True),
                    style=input_card_style,
                    **class_name_kwarg,
                ),
                dbc.Col(dbc.Card(children=output_card_children)),
            ],
        )


class DbcSidebar(BaseDbcTemplate):
    def __init__(self, title=None, sidebar_columns=4, **kwargs):
        super().__init__(**kwargs)
        self.title = title
        self.sidebar_columns = sidebar_columns

    def _perform_layout(self):
        import dash_bootstrap_components as dbc

        children = []

        if self.title:
            children.extend(
                [
                    html.H3(
                        className="bg-primary text-white",
                        children=self.title,
                        style={"padding": "0.5rem"},
                    ),
                ]
            )

        sidebar_card_style = {"border-radius": 0}

        row = dbc.Row(
            align="top",
            style={"padding": "10px", "margin": "0"},
            children=[
                dbc.Col(
                    children=dbc.Card(
                        children=self.get_containers("input"),
                        body=True,
                    ),
                    style=sidebar_card_style,
                    **filter_kwargs(md=self.sidebar_columns),
                ),
                dbc.Col(
                    children=self.get_containers("output"),
                ),
            ],
        )
        children.append(row)
        return children

    @classmethod
    def _wrap_layout(cls, layout):
        import dash_bootstrap_components as dbc

        return dbc.Container(layout, fluid=True, style={"padding": 0})
