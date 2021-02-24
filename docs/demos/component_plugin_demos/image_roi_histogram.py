import dash
import dash_express as dx
from skimage import data

img = data.camera()

app = dash.Dash(__name__, plugins=[dx.Plugin()])
tp = dx.templates.DbcSidebar(title="Image Intensity Explorer")
img_plugin = dx.component_plugins.GreyscaleImageHistogramROI(img, template=tp)


@app.callback(
    args=img_plugin.args,
    output=img_plugin.output,
    template=tp
)
def callback(plugin_inputs):
    return img_plugin.build(plugin_inputs)


app.layout = tp.layout(app)


if __name__ == "__main__":
    app.run_server(debug=True)
