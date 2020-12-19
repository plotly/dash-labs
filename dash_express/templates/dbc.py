from dash.dependencies import Input

from dash_express.templates.base import BaseTemplateInstance
import dash_html_components as html
from .util import build_id, filter_kwargs, build_component_id


class BaseDbcTemplateInstance(BaseTemplateInstance):
    _inline_css = """
            <style>
            .dcc-slider {
                padding: 12px 20px 12px 20px !important;
                border: 1px solid #ced4da;
                border-radius: .25rem;
             }
            </style>"""

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    # Methods designed to be overridden by subclasses
    @classmethod
    def build_dropdown(cls, options, value=None, clearable=False, name=None, **kwargs):
        import dash_bootstrap_components as dbc

        if not options:
            raise ValueError("Options may not be empty")

        if isinstance(options[0], str):
            options = [{"label": opt, "value": opt} for opt in options]
        else:
            options = list(options)

        if clearable:
            options.insert(0, {"label": "", "value": ""})

        if value is None and clearable is False:
            value = options[0]["value"]

        return dbc.Select(
            id=build_component_id(kind="dropdown", name=name),
            options=options,
            value=value,
        )

    @classmethod
    def build_input(cls, value=None, name=None, **kwargs):
        import dash_bootstrap_components as dbc
        return dbc.Input(
            id=build_component_id(kind="input", name=name),
            value=value,
            **kwargs
        )

    @classmethod
    def build_checkbox(cls, option, value=None, name=None, **kwargs):
        import dash_bootstrap_components as dbc
        if isinstance(option, str):
            option = {"label": option, "value": option}

        return dbc.Checklist(
            id=build_component_id(kind="checkbox", name=name),
            options=[option],
            value=value if value is not None else option["value"],
            **filter_kwargs(**kwargs)
        )

    @classmethod
    def build_optional_component(self, component, enabled=True):
        """ Should come before labeling """
        import dash_bootstrap_components as dbc
        component.id["disable_link"] = component.id["id"]
        component.id["disable_link_prop"] = "checked"
        checkbox_id = build_component_id(
            disable_link=component.id["id"], disable_link_prop="disabled",
            kind="disable-checkbox", name=str(component.id["name"]) + "-enabled",
        )

        input_group = dbc.InputGroup(
            [
                dbc.InputGroupAddon(dbc.Checkbox(
                    id=checkbox_id, checked=enabled
                ), addon_type="prepend"),
                html.Div(style=dict(flex="auto"), children=component)
            ]
        )
        return input_group, checkbox_id, "checked"

    @classmethod
    def build_labeled_component(cls, component, label_id, initial_value):
        import dash_bootstrap_components as dbc
        layout_component = dbc.FormGroup(
            children=[
                dbc.Label(id=label_id, children=[initial_value]),
                component,
            ]
        )

        return layout_component, "children"

    @classmethod
    def _configure_app(cls, app):
        super()._configure_app(app)
        import dash_bootstrap_components as dbc
        # Check if there are any bootstrap css themes already added
        add_theme = True
        for url in app.config.external_stylesheets:
            if "bootstrapcdn" in url:
                add_theme = False
                break
        if add_theme:
            app.config.external_stylesheets.append(dbc.themes.BOOTSTRAP)


class DbcCard(BaseDbcTemplateInstance):
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


class DbcRow(BaseDbcTemplateInstance):
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


class DbcSidebar(BaseDbcTemplateInstance):
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
            align="top",
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

    def maybe_wrap_layout(self, layout):
        import dash_bootstrap_components as dbc
        if self.full:
            return dbc.Container(layout, fluid=True)
        else:
            return layout
