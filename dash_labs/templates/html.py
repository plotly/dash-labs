from dash_labs.templates.base import BaseTemplate
import dash_html_components as html


class HtmlCard(BaseTemplate):
    """
    Simple template that places all components in a few html Div elements with a
    card-like border.
    """

    _valid_locations = ("bottom", "top")
    _default_input_location = "bottom"
    _default_output_location = "top"

    def __init__(self, app, title=None, width=None):
        super().__init__(app)
        self.title = title
        self.width = width

    def _perform_layout(self):
        # No callbacks here. Must be constant or idempotent
        children = []
        if self.title:
            children.append(html.H2(self.title))

        children.append(html.Div(self.get_containers("top")))
        children.append(html.Hr())
        children.append(html.Div(self.get_containers("bottom")))
        layout = html.Div(
            style={
                "width": self.width,
                "border": "1px solid lightgray",
                "padding": 10,
                "border-radius": "6px",
            },
            children=html.Div(children=children),
        )
        return layout
