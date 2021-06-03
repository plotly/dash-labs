from dash_labs import build_id
from dash_labs.dependency import Output, Input
from dash_labs.templates import FlatDiv
from .base import ComponentPlugin
import plotly.graph_objects as go
import dash
from dash.development.base_component import Component


class GreyscaleImageROI(ComponentPlugin):
    """
    Plugin that supports drawing, and editing, a rectangular box on a greyscale image
    and retrieving the selected region and selected pixels.
    """

    def __init__(
        self,
        img,
        template=None,
        image_label=None,
        newshape=None,
        title=None,
        location=Component.UNDEFINED,
        fig_update_callback=None,
    ):
        import plotly.express as px

        if template is None:
            template = FlatDiv(None)

        self.img = img

        if newshape is None:
            newshape = dict(
                fillcolor="lightgray", opacity=0.2, line=dict(color="black", width=8)
            )

        self.newshape = newshape
        self.fig_update_callback = fig_update_callback

        top_margin = 60 if title is not None else 20

        self.image_fig = px.imshow(img, binary_string=True).update_layout(
            dragmode="drawrect",
            margin=dict(l=20, b=20, r=20, t=top_margin),
            newshape=self.newshape,
            title_text=title,
        )

        self.image_graph_id = build_id("image-graph")
        self.histogram_graph_id = build_id("histogram-graph")
        self.image_label = image_label

        # Initialize args component dependencies
        args = template.new_graph(
            self.image_fig,
            component_property="relayoutData",
            kind=Input,
            location=location,
            id=self.image_graph_id,
            label=self.image_label,
        )

        output = {"image_figure": Output(self.image_graph_id, "figure")}

        super().__init__(args, output, template)

    def get_output_values(self, args_value, title=None):
        relayout_data = args_value
        if relayout_data:
            # shape coordinates are floats, we need to convert to ints for slicing
            bounds = self._extract_pixel_bounds_from_shape(relayout_data)
            if bounds is None:
                return {
                    "image_figure": dash.no_update,
                }

            x0, y0, x1, y1 = bounds
            shapes = self._make_rect(x0, y0, x1, y1)

            top_margin = 60 if title is not None else 20

            new_image_fig = go.Figure(self.image_fig)
            new_image_fig.update_layout(
                shapes=shapes,
                margin_t=top_margin,
            )

            if title is not None:
                new_image_fig.update_layout(title_text=title)

            return {
                "image_figure": new_image_fig,
            }
        else:
            return {
                "image_figure": dash.no_update,
            }

    def get_rect_bounds(self, args_value, integer=True):
        """
        :param args_value: grouping of values corresponding to the dependency
            grouping returned by the args property
        :param integer: If True (default), convert bounds into integer pixel
            coordinates. If False, return floating point bounds
        :return: Bounds tuple of the form (x0, y0, x1, y1), or None if no box shape
            is present
        """
        relayout_data = args_value
        if relayout_data:
            bounds = self._extract_pixel_bounds_from_shape(relayout_data)
            if integer and bounds is not None:
                bounds = tuple([int(b) if b is not None else None for b in bounds])
            return bounds
        else:
            return None

    def get_image_slice(self, args_value):
        """
        :param args_value: grouping of values corresponding to the dependency
            grouping returned by the args property
        :return: Slice of the original image that is inside the current bounds, or
            None if no box shape present
        """
        relayout_data = args_value
        if relayout_data:
            bounds = self._extract_pixel_bounds_from_shape(relayout_data)

            if bounds is not None:
                x0, y0, x1, y1 = bounds
                return self.img[int(y0) : int(y1), int(x0) : int(x1)]
            else:
                return None
        else:
            return None

    def _make_rect(self, x0, y0, x1, y1):
        if all((x0, y0, x1, y1)):
            return [
                dict(
                    {
                        "editable": True,
                        "type": "rect",
                        "x0": x0,
                        "y0": y0,
                        "x1": x1,
                        "y1": y1,
                    },
                    **self.newshape
                )
            ]
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

        if all(b is None for b in (x0, y0, x1, y1)):
            return None
        else:
            return x0, y0, x1, y1
