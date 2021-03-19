# The Component Plugin design pattern
Here is a proposed architecture that can be used to extract component creation and callback behavior into a separate class.  The `ComponentPlugin` class encapsulates the creation of inputs and output components, and the generation of output property value functionality.

Here are the most important methods in the `ComponentPlugin` interface

```python
class ComponentPlugin:
    def __init__(self, config, ...):
        pass

    @property
    def args(self):
        raise NotImplementedError

    @property
    def output(self):
        raise NotImplementedError

    @property
    def get_output_values(self, args_value):
        raise NotImplementedError
```

To make use of a `ComponentPlugin` subclass as a part of a callback, plugin users would use the following pattern:

```python
...
plugin = FancyPlugin(**plugin_config)

@app.callback(
    inputs={
        input1=...,
        input2=...,
        plugin_values=plugin.args,
    },
    outputs=[output1, plugin.output],
    template=tpl,
)
def hello_plugin(input1, input2, plugin_values):
    # Do stuff with input1 and inputs2 to build result1 and, optionally,
    # opts
    return result, plugin.get_output_values(plugin_values, **opts)
    
...
```

The ability to pass components to `@app.callback` allows plugins to define their own input and output components, as well as define dependencies to make it possible to both input and output properties of the same component.  Following this pattern, the plugins do not need to define their own callbacks, making it much easier to compose plugins and connect them with custom functionality.

The tuple/dict grouping feature of `@app.callback` allow plugins to store any number of input and output components and make them look like a single value to the user. e.g. `plugin.args` and `plugin_values` above can be dictionaries with any number of keys, but the user can treat them as a single scalar value, so that they can always follow the same usage pattern.

## Component plugin example: DataTablePlugin
Here is an example of a fairly sophisticated plugin for displaying a `DataTable`. This plugin supports table paging, sorting, and filtering, and can be configured to operate in either clientside or serverside configurations.  While the clientside and serverside configuration logic is very different, involving different callback properties, the user can switch between these modes using a single constructor argument.

The clientside functionality is taken from https://dash.plotly.com/datatable/interactivity, and the serverside functionality is taken from https://dash.plotly.com/datatable/callbacks. 

Here is an example of an app that uses this plugin to create a `DataTable` that supports serverside paging, sorting, and filtering.

Note that the DataFrame that is input to the DataTable is first filtered using a Dropdown on the `sex` column of the dataset. This is an example of how plugins can support integration with the external logic of a callback. 

[demos/component_plugin_demos/datatable_component_plugin.py](./demos/component_plugin_demos/datatable_component_plugin.py)

```python
import plotly.express as px
import dash_labs as dl
import dash

df = px.data.tips()

app = dash.Dash(__name__, plugins=[dl.Plugin()])
tpl = dl.templates.DbcCard(title="Table Component Plugin")

# serverside = False
serverside = True
table_plugin = dl.component_plugins.DataTablePlugin(
    df=df, page_size=10, sort_mode="single", filterable=True,
    serverside=serverside, template=tpl
)

@app.callback(
    args=[
        tpl.dropdown_input(["Male", "Female"], label="Patron Gender", clearable=True),
        table_plugin.args
    ],
    output=table_plugin.output,
    template=tpl,
)
def callback(gender, plugin_input):
    if gender:
        filtered_df = df.query(f"sex == {repr(gender)}")
    else:
        filtered_df = df
    return table_plugin.get_output_values(plugin_input, filtered_df)

app.layout = tpl.layout(app)

if __name__ == "__main__":
    app.run_server(debug=True)
```
![](https://i.imgur.com/2gsF4rC.gif)

And here is an example of using the same plugin to display the contents of the table (post filtering) in a plotly express figure:

[demos/component_plugin_demos/datatable_component_plugin_and_graph.py](./demos/component_plugin_demos/datatable_component_plugin_and_graph.py)

```python
import plotly.express as px
import dash_labs as dl
import dash
import plotly.io as pio

df = px.data.tips()

app = dash.Dash(__name__, plugins=[dl.Plugin()])
tpl = dl.templates.DbcCard(
    title="Table Component Plugin",
    figure_template=True
)

serverside = True
table_plugin = dl.component_plugins.DataTablePlugin(
    df=df, page_size=10, template=tpl, sort_mode="single", filterable=True,
    serverside=serverside
)

@app.callback(
    args=[
        tpl.dropdown_input(["Male", "Female"], label="Patron Gender", clearable=True),
        table_plugin.args
    ],
    output=[table_plugin.output, tpl.graph_output()],
    template=tpl,
)
def callback(gender, table_input):
    if gender:
        filtered_df = df.query(f"sex == {repr(gender)}")
    else:
        filtered_df = df

    dff = table_plugin.get_processed_dataframe(table_input, filtered_df)

    colorway = pio.templates[pio.templates.default].layout.colorway
    fig = px.scatter(
        dff, x="total_bill", y="tip", color="sex",
        color_discrete_map={
            "Male": colorway[0], "Female": colorway[1]
        },
    )

    return [table_plugin.get_output_values(table_input, dff, preprocessed=True), fig]

app.layout = tpl.layout(app)

if __name__ == "__main__":
   app.run_server(debug=True)
```

![](https://i.imgur.com/12burki.gif)

The `DataTablePlugin.get_processed_dataframe` method applies all serverside filtering and sorting to the input DataFrame, allowing the callback to use this data in a plotly express figure.  The example passes the preprocessed DataFrame, `dff`, to `get_output_values`. As a performance optimization, because we know that this DataFrame has already been preprocessed there is no nee for `get_output_values` to perform this preprocessing a second time.  Setting `preprocessed=True` tells `get_output_values` to skip the preprocessing step and display the input DataFrame as-is. 

## Component plugin example: Image shape drawing
Here is a ComponentPlugin implementation of a shape drawing app similar to that described in https://dash.plotly.com/annotations. This Plugin displays a greyscale image in a plotly figure that is configured to draw rectangle shapes on drag.  The current rectangle can also be edited by clicking it to activate shape editing more.

The plugin proves helper methods to extract the current bounds (if any) of the active rectangle (`get_rect_bounds`), and to extract the selected slice of the original image (`get_image_slice`). The `get_output_values` method supports a `title` argument that can be used to add a custom title to the resulting figure.
 
Here is an example that simply sets the title to the coordinates of the current rectangle bounds

```python
import dash
import dash_labs as dl
from skimage import data

img = data.camera()

app = dash.Dash(__name__, plugins=[dl.Plugin()])
tpl = dl.templates.DbcCard(title="Image Intensity Explorer", columns=4)
img_plugin = dl.component_plugins.GreyscaleImageROI(img, template=tpl, title="Bounds:")


@app.callback(args=[img_plugin.args], output=img_plugin.output, template=tpl)
def callback(inputs_value):
    bounds = img_plugin.get_rect_bounds(inputs_value)
    title = "Bounds: {}".format(bounds)
    return img_plugin.get_output_values(inputs_value, title=title)


app.layout = tpl.layout(app)

if __name__ == "__main__":
    app.run_server(debug=True)
```

And here is an example that uses `get_image_slice` to extract the pixels within the rectangle and display their intensities in a histogram.

[demos/component_plugin_demos/image_roi_histogram.py](./demos/component_plugin_demos/image_roi_histogram.py)

```python
import dash
import dash_labs as dl
from skimage import data
import plotly.express as px

img = data.camera()

app = dash.Dash(__name__, plugins=[dl.Plugin()])
tpl = dl.templates.DbcSidebar(
    title="Image Intensity Explorer",
    sidebar_columns=4,
)

img_plugin = dl.component_plugins.GreyscaleImageROI(img, template=tpl, title="Bounds:")


@app.callback(
    args=[img_plugin.args], output=[img_plugin.output, tpl.graph_output()], template=tpl
)
def callback(inputs_value):
    bounds = img_plugin.get_rect_bounds(inputs_value)
    img_slice = img_plugin.get_image_slice(inputs_value)
    if img_slice is not None:
        hist_figure = (
            px.histogram(img_slice.ravel())
            .update_layout(title_text="Intensity", showlegend=False)
            .update_xaxes(range=[0, 255])
        )
    else:
        hist_figure = {}

    title = "Bounds: {}".format(bounds)
    return [img_plugin.get_output_values(inputs_value, title=title), hist_figure]


app.layout = tpl.layout(app)


if __name__ == "__main__":
    app.run_server(debug=True)
```

## Component Plugin Example: Dynamic Label
Here is a component plugin that can be used to display a dynamic label for a component using its current value and a format string.

[demos/component_plugin_demos/dynamic_input_plugin.py](./demos/component_plugin_demos/dynamic_input_plugin.py)

```python
import dash
import dash_labs as dl
import numpy as np
import plotly.express as px

app = dash.Dash(__name__, plugins=[dl.Plugin()])

tpl = dl.templates.DbcSidebar(title="Dynamic Label Plugin")

phase_plugin = dl.component_plugins.DynamicInputPlugin(
    tpl.slider_input(1, 10, value=4, label="Phase: {:.1f}", tooltip=False), template=tpl
)

@app.callback(
    args=dict(
        fun=tpl.dropdown_input(["sin", "cos", "exp"], label="Function"),
        phase_inputs=phase_plugin.args,
    ),
    output=[tpl.graph_output(), phase_plugin.output],
    template=tpl,
)
def callback(fun, phase_inputs):
    phase = phase_plugin.get_value(phase_inputs)
    xs = np.linspace(-10, 10, 100)
    fig = px.line(x=xs, y=getattr(np, fun)(xs + phase)).update_layout()

    return [fig, phase_plugin.get_output_values(phase_inputs)]


app.layout = tpl.layout(app)

if __name__ == "__main__":
    app.run_server(debug=True)
```

![](https://i.imgur.com/pbHCvtV.gif)
