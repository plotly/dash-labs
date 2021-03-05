from dash.development.base_component import Component

from dash_labs.templates.base import BaseTemplate
import dash_html_components as html
from dash_labs.util import filter_kwargs, build_id
from dash_labs.dependency import Input, Output
import plotly.graph_objects as go
import copy
import plotly.io as pio


class BaseDbcTemplate(BaseTemplate):
    # - Align sliders vertically with an outline that matches dropdowns/inputs
    # - Undo the negative margins that table rows pick up from bootstrap's own row
    #   CSS class. Otherwise, table expand in width outside of their container.
    _inline_css = """
            <style>
             
             .dash-spreadsheet .row {
                margin-left: 0;
                margin-right: 0;
             }
             
             .dash-spreadsheet th {
                background-color: var(--primary) !important;
                color: var(--white) !important;
                border-color: rgba(128, 128, 128, 0.3) !important;
                font-weight: 400 !important;
                font-size: 1.25em !important;
             }
             
             .dash-spreadsheet td {
                background-color: var(--light) !important;
                border-color: rgba(128, 128, 128, 0.3) !important;
                color: var(--dark) !important;
             }
             
             .dash-spreadsheet tr:hover td {
                border-color: lightgrey !important;
                border-width: 0.5px !important;
                background-color: var(--info) !important;
                color: white !important;
             }
             
             .param-markdown > p {
                margin-bottom: 0.5rem;
             }
             .param-markdown > p:last-of-type {
                margin-bottom: 0;
             }
             
             .tab-pane .card {
                border-top-left-radius: 0;
             }
             
             .nav-tabs {
                border-bottom-width: 0 !important;
             }
             
             .nav-link {
                border-width: 0.5px !important;
                border-color: rgba(128, 128, 128, 0.3) !important;
             }
             
             .nav-link.active {
                background-color: var(--primary) !important;
                color: var(--white) !important;
                border-color: rgba(0, 0, 0, 0.125);
             }
             
             .nav-item {
                margin-right: 0 !important;
             }
             
             .card {
                margin-bottom: 1rem !important;
            }
            </style>"""

    def __init__(self, theme=None, **kwargs):
        super().__init__()
        self.theme = theme

    # Methods designed to be overridden by subclasses
    @classmethod
    def button_input(
            cls, children, label=Component.UNDEFINED, role=Component.UNDEFINED,
            component_property="n_clicks", kind=Input, id=None, opts=None
    ):
        import dash_bootstrap_components as dbc

        return kind(
            dbc.Button(children=children, **filter_kwargs(opts, id=id)),
            component_property=component_property, label=label, role=role
        )

    @classmethod
    def dropdown_input(
            cls, options, value=Component.UNDEFINED, clearable=False,
            label=Component.UNDEFINED, role=Component.UNDEFINED,
            component_property="value", kind=Input, id=None, opts=None
    ):
        import dash_bootstrap_components as dbc

        if isinstance(options, list) and options and not isinstance(options[0], dict):
            options = [{"value": opt, "label": opt} for opt in options]

        if clearable:
            options.insert(0, {"value": "", "label": "<Clear>"})

        # Set starting value if not specified
        if value is Component.UNDEFINED and options:
            value = options[0]["value"]

        # classname
        opts = opts or {}
        opts.setdefault("className", "h6")

        return kind(
            dbc.Select(options=options, **filter_kwargs(opts, value=value, id=id)),
            component_property=component_property, label=label, role=role
        )

    @classmethod
    def textbox_input(
            cls, value=None,
            label=Component.UNDEFINED, role=Component.UNDEFINED,
            component_property="value", kind=Input, id=None, opts=None
    ):
        import dash_bootstrap_components as dbc

        # classname
        opts = opts or {}
        opts.setdefault("className", "h6")

        return kind(
            dbc.Input(value=value, **filter_kwargs(opts, id=id)),
            component_property=component_property, label=label, role=role
        )

    @classmethod
    def checklist_input(
            cls, options, value=None,
            label=Component.UNDEFINED, role=Component.UNDEFINED,
            component_property="value", kind=Input, id=None, opts=None
    ):
        import dash_bootstrap_components as dbc

        if isinstance(options, list) and options and not isinstance(options[0], dict):
            options = [{"value": opt, "label": opt} for opt in options]

        # classname
        opts = opts or {}
        # opts.setdefault("className", "h6")
        # opts.setdefault("className", "btn")

        return kind(
            dbc.Checklist(options=options, **filter_kwargs(opts, value=value, id=id)),
            component_property=component_property, label=label, role=role
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
    def build_labeled_component(cls, component, initial_value, label_id=None):
        import dash_bootstrap_components as dbc

        if not label_id:
            label_id = build_id("label")

        label = dbc.Label(
            id=label_id,
            children=[initial_value],
            style={"display": "block"},
            className="h5",
        )
        container_id = build_id("container")
        container = dbc.FormGroup(id=container_id, children=[label, component])
        return container, "children", label, "children"


    @classmethod
    def build_containered_component(cls, component):
        import dash_bootstrap_components as dbc

        container_id = build_id("container")
        container = dbc.FormGroup(id=container_id, children=[component])
        return container, "children"

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
                theme = dbc.themes.BOOTSTRAP
            else:
                theme = self.theme

            app.config.external_stylesheets.append(theme)

            template = _try_build_plotly_template_from_bootstrap_css_url(theme)
            if template is not None:
                pio.templates.default = template


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
        output_containers = self.get_containers("output")
        if output_containers:
            card_body_children.extend(output_containers)
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
                    children=dbc.Card(
                        children=self.get_containers("output"),
                        body=True
                    )
                ),
            ],
        )
        children.append(row)
        return children

    @classmethod
    def _wrap_layout(cls, layout):
        import dash_bootstrap_components as dbc

        return dbc.Container(layout, fluid=True, style={"padding": 0})


class DbcSidebarTabs(BaseDbcTemplate):
    def __init__(self, tab_roles, title=None, sidebar_columns=4, **kwargs):
        import dash_bootstrap_components as dbc

        # Set valid roles before constructor
        self._valid_roles = ["input", "output"] + list(tab_roles)

        super().__init__(**kwargs)
        self.title = title
        self.tab_roles = tab_roles
        self.sidebar_columns = sidebar_columns
        self._tabs = dbc.Tabs(id=build_id("tabs"))

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

        self._tabs.children = [
            dbc.Tab(
                [
                    dbc.Card([
                        ac.container_component
                        for ac in reversed(self.roles[role].values())
                    ], body=True)
                ],
                tab_id=role,
                label=role,
            )
            for role in self.tab_roles
        ]

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
                    md=self.sidebar_columns,
                ),
                dbc.Col(self._tabs, md=12 - self.sidebar_columns),
            ],
        )
        children.append(row)
        return children

    @classmethod
    def _wrap_layout(cls, layout):
        import dash_bootstrap_components as dbc
        return dbc.Container(layout, fluid=True, style={"padding": 0})

    def tab_input(self):
        return Input(self._tabs.id, "active_tab")

def _parse_rules_from_bootstrap_css(css_text):
    import tinycss2
    tinycss_parsed = tinycss2.parse_stylesheet(css_text)

    # Build dict from css selectors to dict of css prop-values
    rule_props = {}
    for token in tinycss_parsed:
        if token.type != "qualified-rule":
            continue
        rule = token
        selector_str = "".join([t.serialize() for t in rule.prelude])
        selectors = tuple(s.strip() for s in selector_str.split(","))
        property_strings = [
            entry for entry in "".join([
                c.serialize().strip()
                for c in rule.content]).split(';')
            if entry
        ]

        property_pairs = [prop_str.split(":") for prop_str in property_strings]
        for selector in selectors:
            for prop_pair in property_pairs:
                if len(prop_pair) != 2:
                    continue
                rule_props.setdefault(selector, {})
                prop_key = prop_pair[0]
                prop_value = prop_pair[1].replace("!important", "").strip()
                rule_props[selector][prop_key] = prop_value

    return rule_props


# Get title font color
def _get_font(rule_props):
    color = "#000"
    family = "sans-serif"

    for el in ["html", "body", "h1"]:
        color = rule_props.get(el, {}).get("color", color)
        family = rule_props.get(el, {}).get("font-family", family)

    return color, family


def _get_role_colors(rule_props):
    # Initialize role_colors with default values
    role_colors = {
        "primary": "#007bff",
        "secondary": "#6c757d",
        "success": "#28a745",
        "info": "#17a2b8",
        "warning": "#ffc107",
        "danger": "#dc3545",
        "light": "#f8f9fa",
        "dark": "#343a40",
    }

    # Override with role colors for current theme
    for prop, val in rule_props[":root"].items():
        if prop.startswith("--"):
            maybe_color = prop.lstrip("-")
            if maybe_color in role_colors:
                role_colors[maybe_color] = val

    return role_colors


def _hex_to_rgb(clr):
    clr = clr.lstrip("#")
    if len(clr) == 3:
        clr = "".join(c[0]*2 for c in clr)
    return tuple(int(clr[i:i+2], 16) for i in (0, 2, 4))


def _to_rgb_tuple(color):
    from plotly.colors import hex_to_rgb, unlabel_rgb
    if isinstance(color, tuple):
        pass
    elif color.startswith("#"):
        color = _hex_to_rgb(color)
    else:
        color = unlabel_rgb(color)

    return tuple(int(c) for c in color)


def _make_grid_color(bg_color, font_color, weight=0.1):
    from plotly.colors import find_intermediate_color, label_rgb
    bg_color = _to_rgb_tuple(bg_color)
    font_color = _to_rgb_tuple(font_color)
    return label_rgb(
        _to_rgb_tuple(find_intermediate_color(bg_color, font_color, weight))
    )


def _build_plotly_template_from_bootstrap_css_text(css_text):
    # Parse css text
    rule_props = _parse_rules_from_bootstrap_css(css_text)

    # Initialize role_colors with default values
    role_colors = _get_role_colors(rule_props)

    # Get font info
    font_color, font_family = _get_font(rule_props)

    # Get background color
    plot_bgcolor = rule_props["body"].get("background-color", "#fff")
    paper_bgcolor = rule_props[".card"].get("background-color", plot_bgcolor)

    # If paper color has transparency, then overlaying on the card won't match the card
    # so use same color as plot background
    if "rgba" in paper_bgcolor and "rgba" not in plot_bgcolor:
        paper_bgcolor = plot_bgcolor

    # paper_bgcolor = plot_bgcolor

    # Build colorway
    colorway_roles = [
        "primary",
        "success",
        "info",
        "warning",
        "danger",
    ]
    colorway = [role_colors[r] for r in colorway_roles]

    # Build grid color
    gridcolor = _make_grid_color(plot_bgcolor, font_color, 0.1)

    # Make template
    template = copy.deepcopy(pio.templates["plotly_dark"])

    layout = template.layout
    layout.colorway = colorway
    layout.piecolorway = colorway
    layout.paper_bgcolor = paper_bgcolor
    layout.plot_bgcolor = plot_bgcolor
    layout.font.color = font_color
    layout.font.family = font_family
    layout.xaxis.gridcolor = gridcolor
    layout.yaxis.gridcolor = gridcolor
    layout.xaxis.gridwidth = 0.5
    layout.yaxis.gridwidth = 0.5
    layout.xaxis.zerolinecolor = gridcolor
    layout.yaxis.zerolinecolor = gridcolor
    layout.margin = dict(l=0, r=0, b=0)

    template.data.scatter = (go.Scatter(marker_line_color=plot_bgcolor),)
    template.data.scattergl = (go.Scattergl(marker_line_color=plot_bgcolor),)

    return template


def _try_build_plotly_template_from_bootstrap_css_url(css_url):
    import requests
    from urllib.parse import urlparse
    parse_result = urlparse(css_url)
    if parse_result.scheme:
        # URL
        response = requests.get(css_url)
        if response.status_code != 200:
            return None
        css_text = response.content.decode("utf8")
    elif parse_result.path:
        # Local file
        with open(parse_result.path, "rt") as f:
            css_text = f.read()

    return _build_plotly_template_from_bootstrap_css_text(css_text)
