import dash
import dash_labs as dl
from skimage import data

img = data.camera()

app = dash.Dash(__name__, plugins=[dl.Plugin()])
tpl = dx.templates.DbcSidebar(title="Image Intensity Explorer")
img_plugin = dx.component_plugins.GreyscaleImageHistogramROI(img, template=tpl)


@app.callback(
    args=img_plugin.args,
    output=img_plugin.output,
    template=tpl
)
def callback(plugin_inputs):
    return img_plugin.build(plugin_inputs)


app.layout = tpl.layout(app)


if __name__ == "__main__":
    app.run_server(debug=True)
