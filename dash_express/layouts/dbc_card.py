from dash_express.component_layout import ComponentLayout
import dash_html_components as html
from .util import build_id
import dash_bootstrap_components as dbc


class CardLayoutDbc(ComponentLayout):

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

    @property
    def layout(self):
        mode = self.config.get("mode", "card")
        if mode == "card":
            return self._card_layout()
        elif mode == "row":
            return self._row_layout()
        else:
            raise ValueError(f"Invalid mode: {mode}")

    def _card_layout(self):
        import dash_bootstrap_components as dbc

        # No callbacks here. Must be constant or idempotent
        card_children = []
        if self.config.get("title", None):
            card_children.append(dbc.CardHeader(self.config["title"]))

        card_body_children = []
        card_body_children.extend(
            self._components['output']
        )
        card_body_children.append(html.Hr())
        card_body_children.extend(
            self._components['input']
        )

        card_children.append(dbc.CardBody(children=card_body_children))

        card_style = {}
        for config_prop in ["width", "height"]:
            if self.config.get(config_prop, None):
                card_style[config_prop] = self.config[config_prop]

        return dbc.Card(
            style=card_style,
            children=card_children
        )

    def _row_layout(self):
        output_card_children = []
        if self.config.get("title", None):
            output_card_children.append(dbc.CardHeader(self.config["title"]))

        output_card_children.extend(self._components['output'])

        return dbc.Row([
            dbc.Col(
                dbc.Card(children=self._components['input'], body=True)
            ),
            dbc.Col(
                dbc.Card(children=output_card_children)
            ),
        ])

    # Methods designed to be overridden by subclasses
    def add_dropdown(self, options, id=None, kind="input", **kwargs):
        import dash_bootstrap_components as dbc

        # Bootstrap dbc.Select
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


ComponentLayout.register_component_layout("dbc_card", CardLayoutDbc)
