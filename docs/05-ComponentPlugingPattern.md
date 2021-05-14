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
import dash_bootstrap_components as dbc
import dash

df = px.data.tips()

app = dash.Dash(__name__, plugins=[dl.plugins.FlexibleCallbacks()])
tpl = dl.templates.DbcCard(app, title="Table Component Plugin")

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

app.layout = dbc.Container(fluid=True, children=tpl.children)

if __name__ == "__main__":
    app.run_server(debug=True)
```
![](https://i.imgur.com/n7vUBRi.gif)

And here is an example of using the same plugin to display the contents of the table (post filtering) in a plotly express figure:

[demos/component_plugin_demos/datatable_component_plugin_and_graph.py](./demos/component_plugin_demos/datatable_component_plugin_and_graph.py)

```python
import plotly.express as px
import dash_labs as dl
import dash_bootstrap_components as dbc
import dash
import plotly.io as pio


df = px.data.tips()

app = dash.Dash(__name__, plugins=[dl.plugins.FlexibleCallbacks()])
tpl = dl.templates.DbcSidebar(
    app, title="Table Component Plugin", sidebar_columns=6, figure_template=True
)

serverside = True
table_plugin = dl.component_plugins.DataTablePlugin(
    df=df,
    page_size=10,
    template=tpl,
    sort_mode="single",
    filterable=True,
    serverside=serverside,
    role="input"
)


@app.callback(
    args=[
        tpl.dropdown_input(["Male", "Female"], label="Patron Gender", clearable=True),
        table_plugin.args,
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
        dff,
        x="total_bill",
        y="tip",
        color="sex",
        color_discrete_map={"Male": colorway[0], "Female": colorway[1]},
    )

    return [table_plugin.get_output_values(table_input, dff, preprocessed=True), fig]

app.layout = dbc.Container(fluid=True, children=tpl.children)

if __name__ == "__main__":
    app.run_server(debug=True)
```

![](https://i.imgur.com/yy6MQyB.gif)

The `DataTablePlugin.get_processed_dataframe` method applies all serverside filtering and sorting to the input DataFrame, allowing the callback to use this data in a plotly express figure.  The example passes the preprocessed DataFrame, `dff`, to `get_output_values`. As a performance optimization, because we know that this DataFrame has already been preprocessed there is no nee for `get_output_values` to perform this preprocessing a second time.  Setting `preprocessed=True` tells `get_output_values` to skip the preprocessing step and display the input DataFrame as-is. 

## Component plugin without callback definition
The Component Plugin interface provides a convenience `install_callback` method that will automatically install a callback to enable the plugin's default behavior.  In the case of the `DataTablePlugin`, this shortcut can be used if the contents of the input `DataFrame` never need to change.

Here is an example of this approach 

[demos/component_plugin_demos/datatable_component_plugin2.py](./demos/component_plugin_demos/datatable_component_plugin2.py)

```python
import plotly.express as px
import dash_labs as dl
import dash_bootstrap_components as dbc
import dash

df = px.data.tips()

app = dash.Dash(__name__, plugins=[dl.plugins.FlexibleCallbacks()])
tpl = dl.templates.DbcCard(app, title="DataTablePlugin")

table_plugin = dl.component_plugins.DataTablePlugin(
    df=df,
    page_size=10,
    sort_mode="single",
    filterable=True,
    serverside=False,
    template=tpl,
)

table_plugin.install_callback(app)
app.layout = dbc.Container(fluid=True, children=tpl.children)

if __name__ == "__main__":
    app.run_server(debug=True)
```

![](https://i.imgur.com/66HhTr7.png)

## Component plugin example: Image shape drawing
Here is a ComponentPlugin implementation of a shape drawing app similar to that described in https://dash.plotly.com/annotations. This Plugin displays a greyscale image in a plotly figure that is configured to draw rectangle shapes on drag.  The current rectangle can also be edited by clicking it to activate shape editing more.

The plugin proves helper methods to extract the current bounds (if any) of the active rectangle (`get_rect_bounds`), and to extract the selected slice of the original image (`get_image_slice`). The `get_output_values` method supports a `title` argument that can be used to add a custom title to the resulting figure.
 
Here is an example that simply sets the title to the coordinates of the current rectangle bounds

[demos/component_plugin_demos/image_roi2.py](./demos/component_plugin_demos/image_roi2.py)

```python
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
```

![](https://i.imgur.com/1QzpmLg.gif)

And here is an example that uses `get_image_slice` to extract the pixels within the rectangle and display their intensities in a histogram.

[demos/component_plugin_demos/image_roi_histogram.py](./demos/component_plugin_demos/image_roi_histogram.py)

```python
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


app.layout = dbc.Container(fluid=True, children=tpl.children)


if __name__ == "__main__":
    app.run_server(debug=True)
```

![](https://i.imgur.com/k9ZeOa9.gif)

## Component Plugin Example: Dynamic Label
Here is a component plugin that can be used to display a dynamic label for a component using its current value and a format string.

[demos/component_plugin_demos/dynamic_label_plugin.py](./demos/component_plugin_demos/dynamic_label_plugin.py)

```python
import dash
import dash_labs as dl
import dash_bootstrap_components as dbc
import numpy as np
import plotly.express as px

app = dash.Dash(__name__, plugins=[dl.plugins.FlexibleCallbacks()])

tpl = dl.templates.DbcSidebar(app, title="Dynamic Label Plugin", figure_template=True)
phase_plugin = dl.component_plugins.DynamicLabelPlugin(
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
    fig = px.line(x=xs, y=getattr(np, fun)(xs + phase), title="Function Value")

    return [fig, phase_plugin.get_output_values(phase_inputs)]

app.layout = dbc.Container(fluid=True, children=tpl.children)

if __name__ == "__main__":
    app.run_server(debug=True)
```

## Example of combining plugins
Here is a more sophisticated example that combines
 - `DbcSidebarTabs` template with `DARKLY` bootstrap theme
 - Label in sidebar displays the name of the current active tab
 - `DynamicLabelPlugin` is used to display the current slider value
 - `DataTablePlugin` is used to display a serverside `DataTable` in a tab

[demos/component_plugin_demos/bootstrap_themes_tabs_table_dynamic_input.py](./demos/component_plugin_demos/bootstrap_themes_tabs_table_dynamic_input.py)

```python
import dash
import dash_labs as dl
import plotly.express as px
import plotly.graph_objects as go
import dash_bootstrap_components as dbc

app = dash.Dash(__name__, plugins=[dl.plugins.FlexibleCallbacks()])

df = px.data.gapminder()
df = df[[c for c in df.columns if not c.startswith("iso_")]]
years = sorted(df.year.drop_duplicates())
continents = list(df.continent.drop_duplicates())

tabs = dict(scatter="Scatter", hist="Histogram", table="Table")

tpl = dl.templates.DbcSidebarTabs(
    app,
    tabs,
    title=f"Dash Labs App",
    theme=dbc.themes.DARKLY,
    figure_template=True,
)

table_plugin = dl.component_plugins.DataTablePlugin(
    df.iloc[:0],
    sort_mode="single",
    role="table",
    page_size=15,
    serverside=True,
    filterable=True,
)

year_label_plugin = dl.component_plugins.DynamicLabelPlugin(
    tpl.slider_input(
        years[0],
        years[-1],
        step=5,
        value=years[-1],
        label="Year: {}",
        tooltip=False,
    )
)


@app.callback(
    args=dict(
        continent=tpl.checklist_input(continents, value=continents, label="Continents"),
        year_args=year_label_plugin.args,
        logs=tpl.checklist_input(
            ["log(x)"], value="log(x)", label="Axis Scale", role="scatter"
        ),
        table_inputs=table_plugin.args,
        tab=tpl.tab_input(),
    ),
    output=[
        tpl.graph_output(role="scatter"),
        tpl.graph_output(role="hist"),
        table_plugin.output,
        year_label_plugin.output,
        dl.Output(
            dbc.Label(children="Current Tab: ", className="h5"),
            "children",
            role="input",
        ),
    ],
    template=tpl,
)
def callback(year_args, continent, logs, table_inputs, tab):

    # Get year value from plugin
    year = year_label_plugin.get_value(year_args)
    logs = logs or []

    # Let parameterize infer output component
    year_df = df[df.year == year]
    if continent:
        year_df = year_df[year_df.continent.isin(continent)]

    if not len(year_df):
        return [go.Figure(), go.Figure()]

    title = f"Life Expectancy ({year})"
    scatter_fig = (
        px.scatter(
            year_df,
            x="gdpPercap",
            y="lifeExp",
            size="pop",
            color="continent",
            hover_name="country",
            log_x="log(x)" in logs,
            size_max=60,
        )
        .update_layout(title_text=title, margin=dict(l=0, r=0, b=0))
        .update_traces(marker_opacity=0.8)
    )

    hist_fig = px.histogram(
        year_df, x="lifeExp", color="continent", barnorm=""
    ).update_layout(
        title_text=title,
    )

    return (
        scatter_fig,
        hist_fig,
        table_plugin.get_output_values(table_inputs, df=year_df),
        year_label_plugin.get_output_values(year_args),
        "Current Tab: " + tabs[tab],
    )


app.layout = dbc.Container(fluid=True, children=tpl.children)

if __name__ == "__main__":
    app.run_server(debug=True)
```
![](https://i.imgur.com/3DKFgGW.gif)
