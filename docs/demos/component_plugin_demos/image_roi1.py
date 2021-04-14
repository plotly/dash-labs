import dash
import dash_labs as dl
from skimage import data

img = data.camera()

app = dash.Dash(__name__, plugins=[dl.plugins.FlexibleCallbacks()])

img_plugin = dl.component_plugins.GreyscaleImageROI(img)
img_plugin.install_callback(app)
app.layout = img_plugin.container

if __name__ == "__main__":
    app.run_server(debug=True)
