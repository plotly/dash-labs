from dash_express.templates.base import BaseTemplate, BaseTemplateBuilder
import dash_html_components as html
from .util import build_id, filter_kwargs, build_component_id


class BaseDbcTemplate(BaseTemplate):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    # Methods designed to be overridden by subclasses
    @classmethod
    def build_dropdown(cls, options, value=None, index=None, **kwargs):
        import dash_bootstrap_components as dbc

        if not options:
            raise ValueError("Options may not be empty")

        if isinstance(options[0], str):
            options = [{"label": opt, "value": opt} for opt in options]

        return dbc.Select(
            id=build_component_id(kind="dropdown", index=index),
            options=options,
            value=value if value is not None else options[0]["value"],
        )

    @classmethod
    def build_input(cls, value=None, index=None, **kwargs):
        import dash_bootstrap_components as dbc
        return dbc.Input(
            id=build_component_id(kind="input", index=index),
            value=value,
            **kwargs
        )

    @classmethod
    def build_checkbox(cls, option, value=None, index=None, **kwargs):
        import dash_bootstrap_components as dbc
        if isinstance(option, str):
            option = {"label": option, "value": option}

        return dbc.Checklist(
            id=build_component_id(kind="checkbox", index=index),
            options=[option],
            value=value if value is not None else option["value"],
            **filter_kwargs(**kwargs)
        )

    @classmethod
    def build_labeled_component(cls, component, label_id, initial_value):
        import dash_bootstrap_components as dbc

        # Make sure component has block display so label is displayed above input
        # component
        style = getattr(component, "style", {})
        style["display"] = "block"
        component.style = style
        layout_component = dbc.FormGroup(
            children=[
                dbc.Label(id=label_id, children=initial_value),
                component
            ]
        )
        return layout_component, "children"


class DbcCardTemplate(BaseDbcTemplate):
    def __init__(self, title=None, full=True, columns=12, min_width=400, height=None, **kwargs):
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
        card_body_children.extend(
            self._components['output']
        )
        card_body_children.append(html.Hr())
        card_body_children.extend(
            self._components['input']
        )

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


class DbcRowTemplate(BaseDbcTemplate):
    def __init__(
            self, title=None, row_height=None, input_cols=4, min_input_width="300px", **kwargs
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

        output_card_children.extend(self._components['output'])

        input_card_style = {}
        if self.min_input_width is not None:
            input_card_style["min-width"] = self.min_input_width

        row_style = {}
        if self.row_height is not None:
            row_style["height"] = self.row_height

        class_name_kwarg = {}
        if self.input_cols is not None:
            class_name_kwarg["className"] = f"col-{int(self.input_cols)}"

        return dbc.Row(style=row_style, children=[
            dbc.Col(
                children=dbc.Card(
                    children=self._components['input'],
                    body=True
                ),
                style=input_card_style,
                **class_name_kwarg,
            ),
            dbc.Col(
                dbc.Card(children=output_card_children)
            ),
        ])


class DbcSidebarTemplate(BaseDbcTemplate):
    def __init__(
            self, title=None, sidebar_columns=4, **kwargs
    ):
        super().__init__(**kwargs)
        self.title = title
        self.sidebar_columns = sidebar_columns

    def _perform_layout(self):
        import dash_bootstrap_components as dbc
        children = []

        if self.title:
            children.extend([
                html.H3(
                    className="bg-primary text-white",
                    children=self.title,
                    style={"padding": "0.5rem"}
                ),
            ])

        sidebar_card_style = {"border-radius": 0}

        row = dbc.Row(
            align="center",
            children=[
                dbc.Col(
                    children=dbc.Card(
                        children=self._components['input'],
                        body=True,
                    ),
                    style=sidebar_card_style,
                    **filter_kwargs(md=self.sidebar_columns),
                ),
                dbc.Col(
                    children=self._components['output'],
                    style={
                        "padding": "1.25rem"
                    },
                )
            ]
        )
        children.append(row)
        return children

    def _app_wrapper(self, layout):
        import dash_bootstrap_components as dbc
        return dbc.Container(layout, fluid=True)


class BaseDbcTemplateBuilder(BaseTemplateBuilder):
    @classmethod
    def configure_app(cls, app):
        super().configure_app(app)
        import dash_bootstrap_components as dbc
        # Check if there are any bootstrap css themes already added
        add_theme = True
        for url in app.config.external_stylesheets:
            if "bootstrapcdn" in url:
                add_theme = False
                break
        if add_theme:
            app.config.external_stylesheets.append(dbc.themes.BOOTSTRAP)


class DbcCard(BaseDbcTemplateBuilder):
    _template_cls = DbcCardTemplate

    def __init__(self, title=None, columns=12, min_width=400, height=None, **kwargs):
        super().__init__(
            title=title, columns=columns, min_width=min_width, height=height, **kwargs
        )


class DbcSidebar(BaseDbcTemplateBuilder):
    _template_cls = DbcSidebarTemplate

    def __init__(self, title=None, sidebar_columns=4, **kwargs):
        super().__init__(
            title=title, sidebar_columns=sidebar_columns, **kwargs
        )


class DbcRow(BaseDbcTemplateBuilder):
    _template_cls = DbcRowTemplate

    def __init__(
            self, title=None, row_height=None, input_cols=4,
            min_input_width="300px", **kwargs
    ):
        super().__init__(
            title=title, row_height=row_height,
            input_cols=input_cols, min_input_width=min_input_width, **kwargs
        )
