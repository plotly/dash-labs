from dash_express.templates.base import BaseTemplateInstance
import dash_html_components as html
import dash_core_components as dcc
from templates.util import build_id


class DccCard(BaseTemplateInstance):
    _inline_css = """
        <style>
        .dcc-slider {
            padding: 12px 20px 12px 20px !important;
         }
        </style>"""

    def __init__(self, title=None, width=None, **kwargs):
        super().__init__(**kwargs)
        self.title = title
        self.width = width

    def _perform_layout(self):
        # No callbacks here. Must be constant or idempotent
        children = []
        if self.title:
            children.append(html.H2(self.title))
        children.append(html.Div(self._components['output']))
        children.append(html.Hr())
        children.append(html.Div(self._components['input']))
        layout = html.Div(
            style={
                "width": self.width,
                "border": "1px solid lightgray",
                "padding": 10,
                "border-radius": "6px"},
            children=html.Div(children=children)
        )
        return layout

    @classmethod
    def build_optional_component(self, component, enabled=True):
        checkbox_id = build_id(
            kind="disable-checkbox", name=str(component.id["name"]) + "-enabled",
        )

        checklist_value = ["checked"] if enabled else []
        input_group = html.Div(
            style={"display": "flex", "align-items": "center"},
            children=[
                dcc.Checklist(id=checkbox_id, options=[{"label": "", "value": "checked"}], value=checklist_value),
                html.Div(style=dict(flex="auto"), children=component)
            ]
        )
        return input_group, checkbox_id, "value"
