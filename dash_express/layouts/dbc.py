from dash_express.layouts.component_layout import ComponentLayout
import dash_html_components as html
from .util import build_id, filter_kwargs
import dash_bootstrap_components as dbc


class BaseDbcLayout(ComponentLayout):

    def __init__(self, app, *args, **kwargs):
        super().__init__(app, *args, **kwargs)

        # Check if there are any bootstrap css themes already added
        add_theme = True
        for url in app.config.external_stylesheets:
            if "bootstrapcdn" in url:
                add_theme = False
                break
        if add_theme:
            app.config.external_stylesheets.append(dbc.themes.BOOTSTRAP)

    # Methods designed to be overridden by subclasses
    def add_dropdown(self, options, id=None, kind="input", **kwargs):
        import dash_bootstrap_components as dbc

        if not options:
            raise ValueError("Options may not be empty")

        if isinstance(options[0], str):
            options = [{"label": opt, "value": opt} for opt in options]

        component = dbc.Select(
            id=build_id(id, "dropdown"),
            options=options,
            value=options[0]["value"]
        )
        self.add_component(component, kind=kind, **kwargs)
        return component

    def add_input(self, initial_value=None, id=None, kind="input", **kwargs):
        import dash_bootstrap_components as dbc

        component = dbc.Input(
            id=build_id(id, "input"),
            value=initial_value,
        )
        self.add_component(component, kind=kind, **kwargs)
        return component

    def build_labeled_input(self, component, label_id, initial_value):
        import dash_bootstrap_components as dbc
        # Subclass could use bootstrap or ddk
        layout_component = dbc.FormGroup(
            children=[
                dbc.Label(id=label_id, children=initial_value),
                component
            ]
        )
        return layout_component, "children"


class DbcCardLayout(BaseDbcLayout):
    def __init__(self, app, columns=12, min_width=400, height=None, **kwargs):
        super().__init__(app, **kwargs)
        self.columns = columns
        self.height = height
        self.min_width = min_width

    @property
    def layout(self):
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


class DbcRowLayout(BaseDbcLayout):
    def __init__(
            self, app, row_height=None, input_cols=4, min_input_width="300px", **kwargs
    ):
        super().__init__(app, **kwargs)
        self.row_height = row_height
        self.input_cols = input_cols
        self.min_input_width = min_input_width

    @property
    def layout(self):
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


class DbcSidebarLayout(BaseDbcLayout):
    def __init__(
            self, app, sidebar_columns=4, **kwargs
    ):
        super().__init__(app, **kwargs)
        self.sidebar_columns = sidebar_columns

    @property
    def layout(self):
        children = []

        if self.title:
            children.extend([
                html.H1(
                    className="bg-primary text-white",
                    children=self.title,
                    style={"padding": "1rem"}
                ),
            ])

        sidebar_card_style = {"border-radius": 0}

        children.append(
            dbc.Row(
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
                            # "margin-top": 20,
                            "padding": "1.25rem"
                        },
                    )
                ]
            )
        )
        return dbc.Container(children, fluid=True)
