import dash
import dash_labs as dl
import dash_bootstrap_components as dbc
from skimage import data
import plotly.express as px

img = data.camera()

app = dash.Dash(__name__, plugins=[dl.plugins.FlexibleCallbacks()])
tpl = dl.templates.DbcSidebar(
    app,
    title="Image Intensity Explorer",
    sidebar_columns=6,
    figure_template=True,
)

img_plugin = dl.component_plugins.GreyscaleImageROI(img, template=tpl, title="Bounds:")


@app.callback(
    args=[img_plugin.args], output=[img_plugin.output, tpl.graph_output()], template=tpl
)
def callback(inputs_value):
    bounds = img_plugin.get_rect_bounds(inputs_value)
    img_slice = img_plugin.get_image_slice(inputs_value)
    hist_figure = {}
    if img_slice is not None:
        raveled_imge_slice = img_slice.ravel()
        if len(raveled_imge_slice) > 0:
            hist_figure = (
                px.histogram(raveled_imge_slice)
                .update_layout(title_text="Intensity", showlegend=False)
                .update_xaxes(range=[0, 255])
            )

    title = "Bounds: {}".format(bounds)
    return [img_plugin.get_output_values(inputs_value, title=title), hist_figure]


app.layout = dbc.Container(fluid=True, children=tpl.children)


if __name__ == "__main__":
    app.run_server(debug=True)
