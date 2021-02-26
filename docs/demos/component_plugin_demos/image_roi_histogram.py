import dash
import dash_labs as dl
from skimage import data
import plotly.express as px

img = data.camera()

app = dash.Dash(__name__, plugins=[dl.Plugin()])
tpl = dl.templates.DbcSidebar(title="Image Intensity Explorer", columns=4)
img_plugin = dl.component_plugins.GreyscaleImageROI(
    img, template=tpl, title="Bounds:"
)


@app.callback(
    args=[img_plugin.args],
    output=[img_plugin.output, tpl.graph_output()],
    template=tpl
)
def callback(inputs_value):
    bounds = img_plugin.get_rect_bounds(inputs_value)
    img_slice = img_plugin.get_image_slice(inputs_value)
    if img_slice is not None:
        hist_figure = px.histogram(
            img_slice.ravel()
        ).update_layout(
            title_text="Intensity", showlegend=False
        ).update_xaxes(range=[0, 255])
    else:
        hist_figure = {}

    title = "Bounds: {}".format(bounds)
    return [
        img_plugin.get_output_values(inputs_value, title=title),
        hist_figure
    ]


app.layout = tpl.layout(app)


if __name__ == "__main__":
    app.run_server(debug=True)
