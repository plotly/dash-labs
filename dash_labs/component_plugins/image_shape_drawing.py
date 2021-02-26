from dash_labs import build_id
from dash_labs.dependency import Output, Input
from .base import ComponentPlugin
import plotly.express as px
import plotly.graph_objects as go
import dash


class GreyscaleImageHistogramROI(ComponentPlugin):
    """
    Support dynamic labels and checkbox to disable input component
    """
    def __init__(
            self, img, template, image_label=None, histogram_label=None, newshape=None
    ):
        self.img = img

        if newshape is None:
            newshape = dict(
                fillcolor="lightgray", opacity=0.2, line=dict(color="black", width=8)
            )

        self.newshape = newshape

        self.image_fig = px.imshow(
            img, binary_string=True
        ).update_layout(
            dragmode="drawrect",
            margin=dict(l=20, b=20, r=20, t=20),
            newshape=self.newshape
        )

        self.image_graph_id = build_id("image-graph")
        self.histogram_graph_id = build_id("histogram-graph")
        self.template = template
        self.image_label = image_label
        self.histogram_label = histogram_label

    def _make_histrogram(self, x0, y0, x1, y1):
        if not all((x0, y0, x1, y1)):
            return {}

        roi_image = self.img[int(y0):int(y1), int(x0):int(x1)]

        return px.histogram(
            roi_image.ravel()
        ).update_layout(
            title_text="Intensity", showlegend=False
        ).update_xaxes(range=[0, 255])

    def _make_rect(self, x0, y0, x1, y1):
        if all(( x0, y0, x1, y1)):
            return [dict({
                "editable": True,
                "type": "rect",
                "x0": x0,
                "y0": y0,
                "x1": x1,
                "y1": y1
            }, **self.newshape)]
        else:
            return []

    def _extract_pixel_bounds_from_shape(self, relayout_data):
        x0, y0, x1, y1 = (None,) * 4
        if "shapes" in relayout_data:
            shape = relayout_data["shapes"][-1]
            x0, y0 = shape["x0"], shape["y0"]
            x1, y1 = shape["x1"], shape["y1"]
        elif any(["shapes" in key for key in relayout_data]):
            x0 = [relayout_data[key] for key in relayout_data if "x0" in key][0]
            x1 = [relayout_data[key] for key in relayout_data if "x1" in key][0]
            y0 = [relayout_data[key] for key in relayout_data if "y0" in key][0]
            y1 = [relayout_data[key] for key in relayout_data if "y1" in key][0]

        # normalize coordinates and clamp to valid image boundaries
        if x0 and x1:
            if x0 > x1:
                x0, x1 = x1, x0
            x0 = 0 if x0 < 0 else x0
            x1 = self.img.shape[1] if x1 > self.img.shape[1] else x1
        if y0 and y1:
            if y0 > y1:
                y0, y1 = y1, y0
            y0 = 0 if y0 < 0 else y0
            y1 = self.img.shape[0] if y1 > self.img.shape[0] else y1

        return x0, y0, x1, y1

    @property
    def args(self):
        return self.template.graph(
            self.image_fig, kind=Input, component_property="relayoutData",
            id=self.image_graph_id, label=self.image_label
        )

    @property
    def output(self):
        return {
            "histogram_figure":
                self.template.graph(
                    id=self.histogram_graph_id, label=self.histogram_label
                ),
            "image_figure": Output(self.image_graph_id, "figure")
        }

    def build(self, inputs_value):
        relayout_data = inputs_value
        if relayout_data:
            # shape coordinates are floats, we need to convert to ints for slicing
            x0, y0, x1, y1 = self._extract_pixel_bounds_from_shape(relayout_data)
            shapes = self._make_rect(x0, y0, x1, y1)

            new_image_fig = go.Figure(
                self.image_fig
            )
            new_image_fig.update_layout(shapes=shapes)

            return {
                "histogram_figure": self._make_histrogram(x0, y0, x1, y1),
                "image_figure": new_image_fig,
            }
        else:
            return {
                "histogram_figure": dash.no_update,
                "image_figure": dash.no_update,
            }
