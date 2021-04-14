import dash
import dash_labs as dl
import numpy as np
import dash_core_components as dcc
import plotly.express as px

app = dash.Dash(__name__, plugins=[dl.plugins.FlexibleCallbacks()])

phase_plugin = dl.component_plugins.DynamicLabelPlugin(
    dl.Input(dcc.Slider(min=1, max=10, value=4), label="Phase: {}")
)

phase_plugin.install_callback(app)

app.layout = phase_plugin.container

if __name__ == "__main__":
    app.run_server(debug=True)
