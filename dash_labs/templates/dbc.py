from collections import OrderedDict

from dash.development.base_component import Component

from dash_labs.templates.base import BaseTemplate
import dash_html_components as html
from dash_labs.util import filter_kwargs, build_id
from dash_labs.dependency import Input
import plotly.graph_objects as go
import copy
import plotly.io as pio


class BaseDbcTemplate(BaseTemplate):
    """
    Base class for templates based on the dash-bootstrap-components library
    """

    # - Undo the negative margins that table rows pick up from bootstrap's own row
    #   CSS class. Otherwise, table expand in width outside of their container.
    # - Style various elements using bootstrap css variables
    _inline_css = (
        BaseTemplate._inline_css
        + """

         .container-fluid {
            padding-left: 0;
            padding-right: 0;
         }

         .dash-spreadsheet .row {
            margin-left: 0;
            margin-right: 0;
         }
         
         .dash-spreadsheet-inner input {
            color: var(--white) !important;
            font-weight: 800 !important;
         }         

         .dash-spreadsheet .dash-header {
            background-color: var(--primary) !important;
            color: var(--white) !important;
            border-color: rgba(128, 128, 128, 0.3) !important;
            font-weight: 400 !important;
            font-size: 1.25em !important;
         }
         
         .dash-spreadsheet .dash-filter {
            background-color: var(--primary) !important;
            border-color: rgba(128, 128, 128, 0.3) !important;
         }
         
         .dash-spreadsheet .dash-filter input {
            color: var(--white) !important;
         }
         
         .dash-spreadsheet td {
            background-color: var(--light) !important;
            border-color: rgba(128, 128, 128, 0.3) !important;
            color: var(--dark) !important;
         }
         
         .dash-table-container .dash-spreadsheet-container .dash-spreadsheet-inner table {
            --hover: transparent !important;
         }
         
         .dash-table-container .dash-spreadsheet-container .dash-spreadsheet-inner td.focused {
            background-color: var(--info) !important;
            color: white !important;
         }
                 
         .dash-spreadsheet td.cell--selected {
            background-color: var(--info) !important;
            color: white !important;
         }

         .tab-pane .card {
            border-top-left-radius: 0;
         }
         
         .nav-tabs {
            border-bottom-width: 0 !important;
         }
         
         .nav-link {
            border-width: 0.5px !important;
            border-color: rgba(100, 100, 100, 0.4) !important;
            color: var(--primary) !important;
         }
         
         .nav-link.active {
            background-color: var(--primary) !important;
            color: var(--white) !important;
            border-color: rgba(100, 100, 100, 0.4);
         }
         
         .nav-item {
            margin-right: 0 !important;
         }
         
         .card {
            margin-bottom: 1rem !important;
            border-color: rgba(100, 100, 100, 0.4);
        }
        
    
        .rc-slider-handle {
            border: solid 2px var(--primary) !important;
        }
        
        .rc-slider-handle:focus {
            box-shadow: unset; !important;
            background-color: var(--primary);
        }
        
        .rc-slider-track {
            background-color: var(--primary);
            height: 2px;
            margin-top: 1px;
        }
        .rc-slider-rail {
            height: 2px;
            margin-top: 1px;
        }
        """
    )

    def __init__(self, app, theme=None, figure_template=False):
        """
        :param app: dash.Dash app instance
        :param theme: Path to a bootstrap theme css file. If not provided, a default
            bootstrap theme will be used.
        :param figure_template: If True, generate a plotly.py figure template from the
            provided (or default) bootstrap theme. Figure templates will adopt the
            colors and fonts of the associated bootstrap theme css file.
        """
        self.theme = theme
        self.figure_template = figure_template
        super().__init__(app)

    # Methods designed to be overridden by subclasses
    @classmethod
    def build_labeled_component(cls, component, label, label_id=None, location=None):
        import dash_bootstrap_components as dbc

        if not label_id:
            label_id = build_id("label")

        label_component = dbc.Label(
            id=label_id,
            children=[label],
            style={"display": "block"},
            className="h5",
        )
        container_id = build_id("container")
        container = dbc.FormGroup(
            id=container_id, children=[label_component, component]
        )
        return container, "children", label_component, "children"

    @classmethod
    def build_containered_component(cls, component, location=None):
        import dash_bootstrap_components as dbc

        container_id = build_id("container")
        container = dbc.FormGroup(id=container_id, children=[component])
        return container, "children"

    def _configure_app(self, app):
        super()._configure_app(app)
        import dash_bootstrap_components as dbc

        # Check if there are any bootstrap css themes already added
        add_theme = True
        theme = self.theme
        for url in app.config.external_stylesheets:
            if "bootstrapcdn" in url:
                add_theme = False
                if theme is None:
                    theme = url
                break

        if add_theme:
            if self.theme is None:
                theme = dbc.themes.FLATLY
            else:
                theme = self.theme

            app.config.external_stylesheets.append(theme)

        if self.figure_template:
            self.make_figure_theme(theme, activate=True)

    @classmethod
    def make_figure_theme(cls, theme, activate=True, raise_on_failure=True):
        template = _try_build_plotly_template_from_bootstrap_css_path(theme)
        if template is None and raise_on_failure:
            raise ValueError(
                f"Failed to construct plotly.py figure theme from bootstrap theme:\n"
                f"   {theme}"
            )
        if activate:
            pio.templates["dash_bootstrap"] = template
            pio.templates.default = "dash_bootstrap"

        return template

    # component dependency constructors
    @classmethod
    def new_button(
        cls,
        children,
        color="secondary",
        size="md",
        outline=False,
        label=Component.UNDEFINED,
        kind=Input,
        location=Component.UNDEFINED,
        component_property="n_clicks",
        id=None,
        opts=None,
    ):
        import dash_bootstrap_components as dbc

        return kind(
            dbc.Button(
                children=children,
                **filter_kwargs(opts, id=id, color=color, size=size, outline=outline),
            ),
            component_property=component_property,
            label=label,
            location=location,
        )

    @classmethod
    def new_dropdown(
        cls,
        options,
        value=Component.UNDEFINED,
        clearable=False,
        label=Component.UNDEFINED,
        kind=Input,
        location=Component.UNDEFINED,
        component_property="value",
        id=None,
        opts=None,
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
            component_property=component_property,
            label=label,
            location=location,
        )

    @classmethod
    def new_textbox(
        cls,
        value=None,
        label=Component.UNDEFINED,
        kind=Input,
        location=Component.UNDEFINED,
        component_property="value",
        id=None,
        opts=None,
    ):
        import dash_bootstrap_components as dbc

        # classname
        opts = opts or {}
        opts.setdefault("className", "h6")

        return kind(
            dbc.Input(value=value, **filter_kwargs(opts, id=id)),
            component_property=component_property,
            label=label,
            location=location,
        )

    @classmethod
    def new_checklist(
        cls,
        options,
        value=None,
        label=Component.UNDEFINED,
        kind=Input,
        location=Component.UNDEFINED,
        component_property="value",
        id=None,
        opts=None,
    ):
        import dash_bootstrap_components as dbc

        if isinstance(options, list) and options and not isinstance(options[0], dict):
            options = [{"value": opt, "label": opt} for opt in options]

        opts = opts or {}

        return kind(
            dbc.Checklist(options=options, **filter_kwargs(opts, value=value, id=id)),
            component_property=component_property,
            label=label,
            location=location,
        )


class DbcCard(BaseDbcTemplate):

    _valid_locations = ("bottom", "top")
    _default_input_location = "bottom"
    _default_output_location = "top"

    def __init__(
        self,
        app,
        title=None,
        columns=None,
        min_width=400,
        height=None,
        margin="10px 10px 10px 10px",
        **kwargs,
    ):
        """
        Template that places all components in a single card

        Supported template locations:
          - "bottom": Bottom region of the card (default for Input components)
          - "top": Top region of the card (default for Output components)

        :param app: dash.Dash app instance
        :param title: Card title
        :param columns: Responsive width of card in columns (out of 12 columns)
        :param min_width: Minimum card width in pixels
        :param height: Fixed height of card or None (default) to let card's height
            expand to contents
        :param margin: CSS margin around row
        """
        self.title = title
        self.columns = columns
        self.height = height
        self.min_width = min_width
        self.margin = margin
        super().__init__(app, **kwargs)

    def _perform_layout(self):
        import dash_bootstrap_components as dbc

        # No callbacks here. Must be constant or idempotent
        card_children = []
        if self.title:
            card_children.append(dbc.CardHeader(self.title, className="h4"))

        card_body_children = []
        top_containers = self.get_containers("top")
        bottom_containers = self.get_containers("bottom")
        card_body_children.extend(top_containers)
        if top_containers and bottom_containers:
            card_body_children.append(html.Hr())
        card_body_children.extend(bottom_containers)

        card_children.append(dbc.CardBody(children=card_body_children))

        card_style = {"padding": 0}
        if self.margin:
            card_style["margin"] = self.margin
        if self.height is not None:
            card_style["height"] = self.height

        if self.min_width is not None:
            card_style["min-width"] = self.min_width

        card = dbc.Card(
            style=card_style,
            children=card_children,
        )

        if self.columns:
            card = dbc.Col(card, md=self.columns)

        return card


class DbcRow(BaseDbcTemplate):

    _valid_locations = ("left", "right")
    _default_input_location = "left"
    _default_output_location = "right"

    def __init__(
        self,
        app,
        title=None,
        row_height=None,
        left_cols=4,
        min_left_width="300px",
        margin="10px 0 10px 0",
        **kwargs,
    ):
        """
        Template that places components in two cards, arranged in a row

        Supported template locations:
          - "left": Left card (default for Input components)
          - "right": Right card (default for Output components)

        :param app: dash.Dash app instance
        :param title: Input card title
        :param left_cols: Responsive width of left card in columns (out of 12 columns)
        :param min_left_width: Minimum width (in pixels) of left card
        :param margin: CSS margin around row
        :param row_height: Fixed height of cards in the row in pixels.
            If None (default) each card will independently determine height based on
            contents.
        """
        self.title = title
        self.row_height = row_height
        self.left_cols = left_cols
        self.min_left_width = min_left_width
        self.margin = margin
        super().__init__(app, **kwargs)

    def _perform_layout(self):
        import dash_bootstrap_components as dbc

        right_card_children = []
        if self.title:
            right_card_children.append(dbc.CardHeader(self.title, className="h4"))

        right_card_children.append(dbc.CardBody(self.get_containers("right")))

        left_card_style = {}
        if self.min_left_width is not None:
            left_card_style["min-width"] = self.min_left_width

        row_style = {}
        if self.margin:
            row_style["margin"] = self.margin
        if self.row_height is not None:
            row_style["height"] = self.row_height

        return dbc.Row(
            style=row_style,
            children=[
                dbc.Col(
                    children=dbc.Card(children=self.get_containers("left"), body=True),
                    style=left_card_style,
                    md=self.left_cols,
                ),
                dbc.Col(
                    dbc.Card(children=right_card_children),
                    md=12 - self.left_cols,
                ),
            ],
        )


class DbcSidebar(BaseDbcTemplate):

    _valid_locations = ("sidebar", "main")
    _default_input_location = "sidebar"
    _default_output_location = "main"

    def __init__(self, app, title=None, sidebar_columns=4, **kwargs):
        """
        Template that includes a title bar, a sidebar, and a responsive card in the
        main area of the app.

        Supported template locations:
          - "sidebar": Left sidebar (default for Input components)
          - "main": Main area to the right of sidebar (default for Output components)

        :param app: dash.Dash app instance
        :param title: Title bar title string
        :param sidebar_columns: Responsive width of input card in columns
            (out of 12 columns)
        """
        self.title = title
        self.sidebar_columns = sidebar_columns
        super().__init__(app, **kwargs)

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
                        children=self.get_containers("sidebar"),
                        body=True,
                    ),
                    style=sidebar_card_style,
                    md=self.sidebar_columns,
                ),
                dbc.Col(
                    children=dbc.Card(children=self.get_containers("main"), body=True),
                    md=12 - self.sidebar_columns,
                ),
            ],
        )
        children.append(row)
        return children


class DbcSidebarTabs(BaseDbcTemplate):
    _default_input_location = "sidebar"

    def __init__(self, app, tab_locations, title=None, sidebar_columns=4, **kwargs):
        """
        Template that includes a title bar, a sidebar, and a set of tabs in the main
        area of the app.

        Supported template locations:
          - "sidebar": Left sidebar (default for Input components)
          - list of locations provided as the tab_locations argument to the template
            constructor. Each location corresponds to a separate tab.
            Note: there is no default location for Output components.

        :param app: dash.Dash app instance
        :param tab_locations: List or dict of strings where each string specifies the name
            of the location corresponding to a single tab. If a list, the location name is
            also be used as the title of the corresponding tab. If a dict, the keys
            become the locations and the values become the tab labels
        :param title: Title bar title string
        :param sidebar_columns: Responsive width of sidebar in columns
            (out of 12 columns)
        """
        import dash_bootstrap_components as dbc

        # Set valid roles before constructor
        self.title = title
        self.sidebar_columns = sidebar_columns
        if isinstance(tab_locations, (list, tuple)):
            self.tab_locations = OrderedDict(
                [(location, location) for location in tab_locations]
            )
        else:
            self.tab_locations = OrderedDict(tab_locations)

        self._valid_locations = ["sidebar"] + list(self.tab_locations.keys())

        first_tab = next(iter(self.tab_locations))
        self._tabs = dbc.Tabs(id=build_id("tabs"), active_tab=first_tab)

        super().__init__(app, **kwargs)

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
                    dbc.Card(
                        children=list(reversed(self.get_containers(location))),
                        body=True,
                    ),
                ],
                tab_id=location,
                label=title,
            )
            for location, title in self.tab_locations.items()
        ]

        row = dbc.Row(
            align="top",
            style={"padding": "10px", "margin": "0"},
            children=[
                dbc.Col(
                    children=dbc.Card(
                        children=self.get_containers("sidebar"),
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

    def tab_input(self, kind=Input):
        """
        Dependency object that can be used to input the active tab
        :param kind: The dependency kind to return. One of dl.Input (default) or
            dl.State.
        :return: Dependency object referencing the active tab
        """
        return kind(self._tabs.id, "active_tab")


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
            entry
            for entry in "".join([c.serialize().strip() for c in rule.content]).split(
                ";"
            )
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

    # Override with location colors for current theme
    for prop, val in rule_props[":root"].items():
        if prop.startswith("--"):
            maybe_color = prop.lstrip("-")
            if maybe_color in role_colors:
                role_colors[maybe_color] = val

    return role_colors


def _build_plotly_template_from_bootstrap_css_text(css_text):
    from dash_labs.templates._colors import (
        make_grid_color,
        separate_colorway,
        maybe_blend,
    )

    # Parse css text
    rule_props = _parse_rules_from_bootstrap_css(css_text)

    # Initialize role_colors with default values
    role_colors = _get_role_colors(rule_props)

    # Get font info
    font_color, font_family = _get_font(rule_props)

    # Get background color
    plot_bgcolor = rule_props["body"].get("background-color", "#fff")
    paper_bgcolor = rule_props[".card"].get("background-color", plot_bgcolor)

    blended = maybe_blend(plot_bgcolor, paper_bgcolor)
    if blended is None:
        # Can't blend, use background color for everything
        paper_bgcolor = plot_bgcolor
    else:
        paper_bgcolor = blended

    # Build colorway
    colorway_roles = [
        "primary",
        "danger",
        "success",
        "warning",
        "info",
    ]
    colorway = [role_colors[r] for r in colorway_roles]
    colorway = separate_colorway(colorway)

    # Build grid color
    gridcolor = make_grid_color(plot_bgcolor, font_color, 0.08)

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


def _try_build_plotly_template_from_bootstrap_css_path(css_url):
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
