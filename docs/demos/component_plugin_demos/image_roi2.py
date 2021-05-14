import dash
import dash_labs as dl
import dash_bootstrap_components as dbc
from skimage import data

img = data.camera()

app = dash.Dash(__name__, plugins=[dl.plugins.FlexibleCallbacks()])
tpl = dl.templates.DbcCard(app, title="Image Intensity Explorer", columns=4)
img_plugin = dl.component_plugins.GreyscaleImageROI(img, template=tpl, title="Bounds:")


@app.callback(args=[img_plugin.args], output=img_plugin.output, template=tpl)
def callback(inputs_value):
    bounds = img_plugin.get_rect_bounds(inputs_value)
    title = "Bounds: {}".format(bounds)
    return img_plugin.get_output_values(inputs_value, title=title)


app.layout = dbc.Container(fluid=True, children=tpl.children)


if __name__ == "__main__":
    app.run_server(debug=True)
