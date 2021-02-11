# Overview
Dash Express is a project to significantly expand the capabilities of the Dash `@app.callback` decorator. This project is beginning its life as a separate package that depends on Dash, but the goal is that the successful ideas from this project will migrate into Dash as part of Dash 2.0.

## Design Goals
Dash Express began with several interdependent design goals:
 - Provide a more concise syntax for generating simple Dash apps that follow a variety of nice looking predefined templates.
 - Make it possible for third-party developers to develop and distribute custom templates
 - Ensure that there is a smooth continuum between concision, and the flexibility of "full Dash". The concise syntax should not be a dead-end, requiring the developer to rewrite the app in order to reach a certain level of sophistication.
 - Improve ability of users to encapsulate and reuse custom interactive component workflows, and make it possible for third-party developers to distribute these as plugins.


# Design
The Dash Express design centers on enhancements to the `@app.callback` decorator, enabled through the application of the `dx.Plugin()` Dash plugin.

> it is recommended to import `dash_express` as `dx`, and this is the convention that will be used throughout this document.
 
As described below, the updated decorator retains all of the functionality of the existing (Dash 1) `@app.callback` decorator, but it also includes the ability to optionally generate components and lay them out according to predefined templates.

The capabilities of the new `@app.callback` decorator can be approached from two sides. First, as a Dash implementation of the ipywidgets [`@interact`](https://ipywidgets.readthedocs.io/en/stable/examples/Using%20Interact.html) feature. Second, as a more flexible extension of the Dash 1 `@app.callback` feature set.  This document will start with the former (Chapters 1 and 2), and then discuss the latter (Chapter 3).

## Enabling the Dash Express plugin
The Dash Express features are enabled by specifying an instance of dx.Plugin when instantiating a Dash app. 

```python
import dash
import dash_express as dx
app = dash.Dash(__name__, plugins=[dx.Plugin()])
```

# Chapter 1: @interact-style app generation
Dash Express makes it possible to generate simple apps directly from the `@app.callback` decorator using a style that is inspired by (though not syntactically compatible with) the [`@interact`](https://ipywidgets.readthedocs.io/en/stable/examples/Using%20Interact.html) decorator.

## Basic Example
In this first example, the `greet` function inputs 4 arguments and outputs a `dcc.Graph` component. The graph's figure is configured by these 4 inputs.  By passing component patterns (called [widget abbreviations](https://ipywidgets.readthedocs.io/en/stable/examples/Using%20Interact.html#Widget-abbreviations) in the ipywidgets documentation), the `@app.callback` decorator is told to construct appropriate Dash components for each input argument.  Supported patterns include:

 - Lists (either lists of strings, or lists of dicts with `value` and `label` keys) are converted to dropdowns
 - Tuples are converted to sliders. First and second value are the min and max. An optional third value is the step size
 - Strings are converted to `Input` boxes
 - Booleans are converted to checkboxes.

> Note: Other patterns are under consideration (e.g. datetime values to date pickers, and DataFrame's to DataTables), but these are more complex because as they would require a preprocessing step to convert the raw Dash component values to specialized Python data structures when calling the callback function.

As mentioned below, the set of available patterns can be extended by the current `Template`.

[docs/demos/basic_decorator.py](docs/demos/basic_decorator.py)
```python
import dash
import dash_express as dx
import numpy as np
import dash_core_components as dcc
import plotly.express as px

app = dash.Dash(__name__, plugins=[dx.Plugin()])

@app.callback(
    inputs=dict(
        fun=dx.arg(["sin", "cos", "exp"]),
        figure_title=dx.arg("Initial Title"),
        phase=dx.arg((1, 10)),
        amplitude=dx.arg((1, 10)),
    ),
)
def greet(fun, figure_title, phase, amplitude):
    xs = np.linspace(-10, 10, 100)
    return dcc.Graph(figure=px.line(
        x=xs, y=getattr(np, fun)(xs + phase) * amplitude
    ).update_layout(title_text=figure_title))


app.layout = greet.layout(app)

if __name__ == "__main__":
    app.run_server(debug=True)
```

The `@app.callback` decorator now returns a class called a `CallbackWrapper`.  This will be covered in more depth later, but the simplest role of this class is to provide a `.layout(app)` method that generates a top-level Dash component that contains all of the generated components, and that is suitable for assignment directly to the `app.layout` property.  This method also configures all of the callbacks necessary to produce the interactive app.  Here's what the end result looks like in this case. 

![](https://i.imgur.com/Kl9Walj.gif)

> **Note:** Since no template was specified, the default `FlatDiv` template was used. This template simply places all of the components, inputs followed by outputs, in a flat `Div` element.  Much better looking templates will be introduced in Chapter 2.

## Customizing labels
As seen above, the new `@app.callback` automatically generates a label for each component it creates.  These labels default to the parameter names when the `inputs` argument is a dictionary, and they default to the positional index of the argument if `inputs` is specified as a list (more on `inputs` as lists in [Chapter 3](#Chapter-3-A-more-flexible-appcallback)).

These labels can be customized by wrapping the input pattern with `dx.arg` and overriding the `label` keyword argument. The following example assigns custom labels to all of the inputs.

[demos/basic_decorator_labels.py](./demos/basic_decorator_labels.py)

```python
import dash
import dash_express as dx
import numpy as np
import dash_core_components as dcc
import plotly.express as px

app = dash.Dash(__name__, plugins=[dx.Plugin()])

@app.callback(
    inputs=dict(
        fun=dx.arg(["sin", "cos", "exp"], label="Function"),
        figure_title=dx.arg("Initial Title", label="Figure Title"),
        phase=dx.arg((1, 10), label="Phase"),
        amplitude=dx.arg((1, 10), label="Amplitude"),
    ),
)
def greet(fun, figure_title, phase, amplitude):
    xs = np.linspace(-10, 10, 100)
    return dcc.Graph(figure=px.line(
        x=xs, y=getattr(np, fun)(xs + phase) * amplitude
    ).update_layout(title_text=figure_title))

app.layout = greet.layout(app)

if __name__ == "__main__":
    app.run_server(debug=True)
```

![](https://i.imgur.com/jLWDuME.png)

## Directly input components for full customization

The parameter pattern grammar is convenient, but it's also pretty limited, both in terms of the number of available components and the component styling. To provide the next level of customization, User-defined components can be provided as well.

This example specifies component instances for the `figure_title` and `phase` arguments with customized styling and default values. It also introduces a new `date` parameter that is concatenated with the title on the figure.

 - `figure_title` is now represented by an `dcc.Input` with a crimson background and white text
 - `phase` is now a dropdown of numbers instead of a slider. This also makes it possible to specify a default value of 4
 - `date` is a `dcc.DatePickerSingle` component which provides the callback function with a date string.

Notice that for the `DatePickerSingle` component, `"date"` is passed as the value of the `props` argument to the `dx.arg` constructor. The `props` argument allows us to specify which property from the component is used as the input value of the callback function. For convenience, the default value of `props` is `"value"`, which is why the `props` argument is not required for the `Input` and `Select` components. 

[demos/specialize_components.py](./demos/specialize_components.py)

```python
import dash
import dash_express as dx
import numpy as np
import dash_core_components as dcc
import dash_bootstrap_components as dbc
import plotly.express as px

app = dash.Dash(__name__, plugins=[dx.Plugin()])

# Function to parameterize
@app.callback(
    inputs=dict(
        fun=dx.arg(["sin", "cos", "exp"], label="Function"),

        # Style input using bootstrap classes
        figure_title=dx.arg(
            dbc.Input(
                type="text", value="Initial Title",
                style={"background-color": "crimson", "color": "white"}
            ),
            label="Figure Title",
        ),

        # Explicitly specify component property. Default is "value"
        phase=dx.arg(
            dbc.Select(
                options=[{"label": i, "value": i} for i in range(1, 10)], value=4
            ),
            label="Phase",
        ),

        # Dropdown instead of default slider
        date=dx.arg(dcc.DatePickerSingle(), props="date", label="Measurement Date")
    ),
)
def callback_components(fun, figure_title, phase, date):
    xs = np.linspace(-10, 10, 100)
    return dcc.Graph(figure=px.line(
        x=xs, y=getattr(np, fun)(xs + int(phase))
    ).update_layout(title_text=figure_title + "-" + str(date)))


app.layout = callback_components.layout(app)

if __name__ == "__main__":
    app.run_server(debug=True)
```

![](https://i.imgur.com/WhRGf0t.gif)

## Input components with multiple values
Some components have multiple properties that could be considered the "value" of the component for the purpose of decorated function. One common example is the `DatePickerRange` component.  For this component, the start date is stored in the `start_date` prop and the end date in the `end_date` prop.  To make it possible to pass both of these values to the function, the `props` argument to `dx.arg` may be a tuple (or dict) of multiple properties.

In this example, a tuple of `("start_date", "end_date")` is specified, which results in a tuple of the corresponding component property values to be passed to the decorated callback function. 

[demos/multi_input_component.py](./demos/multi_input_component.py)

```python
import dash
import dash_express as dx
import plotly.graph_objects as go
import dash_core_components as dcc

app = dash.Dash(__name__, plugins=[dx.Plugin()])

@app.callback(
    inputs=dict(
        figure_title=dx.arg(dcc.Input(value="Figure Title"), label="Graph Title"),
        date_range=dx.arg(
            dcc.DatePickerRange(), props=("start_date", "end_date"), label="Date"
        )
    ),
)
def callback_components(figure_title, date_range):
    start_date, end_date = date_range
    if start_date:
        title = figure_title + ": " + str(start_date) + " to " + str(end_date)
    else:
        title = figure_title

    return dcc.Graph(
        figure=go.Figure(
            layout_title_text=title
        )
    )

app.layout = callback_components.layout(app)

if __name__ == "__main__":
    app.run_server(debug=True)
```

![](https://i.imgur.com/shCO5Pz.gif)

## Manually executed function using state

The ipywidgets `@interact` decorator supports a `manual` argument. When `True`, an update button is automatically added and changes to the other widgets are not applied until the update button is clicked.  This workflow can be replicated with `@app.callback` by adding an `html.Button` component and specifying that all inputs other than the button should be classified as `State` (rather than the default of `Input`).  

By default, arguments specified in the `inputs` argument to `@app.callback` are treated as `Input` dependencies, and those specified in the `state` argument are treated as `State` dependencies.  This behavior can also be overridden using the `kind` argument to `dx.arg`.

Here is a full example of specifying all the components as the `state` argument to `@app.callback`, but overriding the button to be treated as `input` instead with `kind="input"`.

[demos/basic_decorator_labels_state.py](./demos/basic_decorator_labels_state.py)

```python
import dash
import dash_express as dx
import numpy as np
import dash_core_components as dcc
import dash_html_components as html
import plotly.express as px

app = dash.Dash(__name__, plugins=[dx.Plugin()])

@app.callback(
    state=dict(
        fun=dx.arg(["sin", "cos", "exp"], label="Function"),
        figure_title=dx.arg("Initial Title", label="Figure Title"),
        phase=dx.arg((1, 10), label="Phase"),
        amplitude=dx.arg((1, 10), label="Amplitude"),
        n_clicks=dx.arg(html.Button("Update"), props="n_clicks", kind="input")
    ),
)
def greet(fun, figure_title, phase, amplitude, n_clicks):
    xs = np.linspace(-10, 10, 100)
    if fun is None:
        ys = xs
    else:
        ys = getattr(np, fun)(xs + phase) * amplitude

    figure_title = "No Title" if figure_title is None else figure_title
    return dcc.Graph(figure=px.line(
        x=xs, y=ys
    ).update_layout(title_text=figure_title))


app.layout = greet.layout(app)

if __name__ == "__main__":
    app.run_server(debug=True)
```

![](https://i.imgur.com/8cd9KvF.gif)

## Custom output components
The new `@app.callback` decorator no longer requires a caller to explicitly provide the output component that the callback function result will be stored in. The default behavior is to create an output `html.Div` component, and to store all the function results as the `children` property of this `Div`.  However, explicit output components and output props can also be configured using the `output` argument to `@app.callback`.

Here is an example that outputs a string to the `children` property of a `dcc.Markdown` component.


[demos/output_markdown.py](./demos/output_markdown.py)

```python
import dash
import dash_core_components as dcc
import dash_express as dx

app = dash.Dash(__name__, plugins=[dx.Plugin()])

@app.callback(
    inputs={
        "input_text": dx.arg(
            dcc.Textarea(value="## Heading\n"), label="Enter Markdown"
        )
    },
    output=dx.arg(dcc.Markdown(), props="children"),
)
def markdown_preview(input_text):
    return input_text

app.layout = markdown_preview.layout(app)

if __name__ == "__main__":
    app.run_server(debug=True)
```

![](https://i.imgur.com/9PEuHcg.gif)

## Output component inference

For the special case of values being output as the `children` property of an output component (as is the default when `output` is not provided), `@app.callback` will now perform output component inference.  `@app.callback` will examine all such returned values, and for those that are not already simple JSON-compatible objects, it will try to identify an appropriate component with which to display the value. Default inferences include:

 - `go.Figure` to `Graph.figure` (either dcc or ddk depending on the template)
 - `pd.DataFrame` -> `DataTable.data` (either `dash_table` or `ddk` depending on template)

Templates can specify additional output inferences.

## Accessing individual components to build custom layouts

### `CallbackWrapper`
Before discussion of the Template system (Chapter 2), we'll cover how the `@app.callback` decorator can be used to construct the function input components, and define the callbacks, but still maintain full control over the app layout.

As mentioned briefly above, the type of the value returned by the `@app.callback` decorator is a `CallbackWrapper` instance. First of all, as expected of a decorator result, this value can be still called just like the function it wraps.  Additionally, it provides the following attributes:

 - `.template`: A template instance that is capable of laying out the input/constructed components. This defaults to the `FlatDiv` template mentioned above that simply adds everything as children of a single top-level `html.Div` component.
 - `.roles`: This is a dictionary from template "roles" to `OrderedDict`s of `ArgumentComponents` (described below). All templates define at least two roles: `"input"` and `"output"`. By default, all components corresponding to the `@app.callback` `inputs` and `state` arguments are assigned the `"input"` role and therefore are included in the `.roles["input"]` `OrderedDict`. Similarly, all components corresponding to the `@app.callback` `output` argument are assigned the "output" role and therefore are included in the `.roles["output"]` `OrderedDict`.  Templates may define additional roles, and `dx.arg` values can be assigned to these roles using the `role` argument.

A `CallbackWrapper` instance also provides the `.layout(app)` method that we've been using so far to ask the template to generate a layout containing all of the callbacks created or provided components.

### ArgumentComponents

You might think that the values of the `.roles["inputs"]` and `.roles["output"]` dictionaries described above would simply be the components that `@app.callback` created.  The reason it's not quite that simple is that for a single callback function argument, `@app.callback` may create multiple components: One for the input value and one for the label, and both of these may be wrapped in a container component.  Because the caller may want access to any, or all, of these components individually, references to all of these components, and their associated props, are stored in a `ArgumentComponents` instance.  Here are the attributes of `ArgumentComponents`, and an example of why a caller may want to access them.

 - `.arg_component`: This a reference to the innermost component that actually provides the callback function with an input value, which corresponds to the properties stored in `.arg_props` attribute. A caller would want to access this component in order to register additional callback functions to execute when the callback function is updated.
 - `.label_component`: This is the component that displays the label string for the component, where the label text is stored in the `.label_props` property of the component. A caller may want to access this component to customize the label styling, or access the current value of the label string.
 - `.container_component`: This is the outer-most component that contains all the other components described above, where the contained components are stored in the `.container_props` property of the container. This is generally the component that a caller should incorporate when building a custom layout.

This example uses `@app.callback` to create components and install callbacks, constructs a fully custom layout, and defines custom callbacks on the components returned by `@app.callback`. This is loosely based on the Dash Bootstrap Components example at https://dash-bootstrap-components.opensource.faculty.ai/examples/iris/. 

Notice how custom callbacks are applied to the dropdowns returned by `@app.callback` to prevent specifying the same feature as both `x` and `y` values.

[demos/custom_layout_and_callback_integration.py](./demos/custom_layout_and_callback_integration.py)

```python
import dash_express as dx
import plotly.express as px
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output
import dash


# Load data
df = px.data.iris()
feature_cols = [col for col in df.columns if "species" not in col]
feature_labels = [col.replace("_", " ").title() + " (cm)" for col in feature_cols]
feature_options = [
    {"label": label, "value": col} for col, label in zip(feature_cols, feature_labels)
]

# Build app and template
app = dash.Dash(__name__, plugins=[dx.Plugin()])


# Use parameterize to create components
@app.callback(
    inputs=dict(
        x=dcc.Dropdown(options=feature_options, value="sepal_length"),
        y=dcc.Dropdown(options=feature_options, value="sepal_width"),
    ),
)
def iris(x, y):
    return dcc.Graph(
        figure=px.scatter(df, x=x, y=y, color="species"),
    )

# Get references to the dropdowns and register a custom callback to prevent the user
# from setting x and y to the same variable

# Get the dropdown components that were created by parameterize
x_component = iris.roles["input"]["x"].arg_component
y_component = iris.roles["input"]["y"].arg_component


# Define standalone function that computes what values to enable, reuse for both
# dropdowns with app.callback
def filter_options(v):
    """Disable option ability to plot x vs x"""
    return [
        {"label": label, "value": col, "disabled": col == v}
        for col, label in zip(feature_cols, feature_labels)
    ]

app.callback(Output(x_component.id, "options"), [Input(y_component.id, "value")])(
    filter_options
)

app.callback(Output(y_component.id, "options"), [Input(x_component.id, "value")])(
    filter_options
)

# Build a custom layout, using the parameter *containers* (not values as above)
x_container = iris.roles["input"]["x"].container_component
y_container = iris.roles["input"]["y"].container_component
output_container = iris.roles["output"][0].container_component

app.layout = html.Div([
    html.H1("Iris Feature Explorer"),
    html.H2("Select Features"),
    x_container,
    y_container,
    html.Hr(),
    html.H2("Feature Scatter Plot"),
    output_container
])

if __name__ == "__main__":
    app.run_server(debug=True)
```
![](https://i.imgur.com/MX4WaGS.gif)

## Component ids
When an input or output component is generated from a pattern, or for a component instance is passed in without an id, `@app.callback` will create an id of the form `{"uid": "{uuid-value}", "name": "{parameter name or index}"}`. The inclusion of the UID ensures that component id's won't clash when the results of `@app.callback` are integrated into a larger app.

 > Note: a fixed random seed is used to ensure that the UUID's generated during app construction are deterministic across app instances

# Chapter 2: Template system
As noted above, the `.layout(app)` method of a `CallbackWrapper` instance builds a Dash component layout that displays all of the generated and provided components.  This layout is customized using templates.

For a caller, specifying a template is simply a matter of proving a template instance as the `template` argument to `@app.callback`.  Built-in templates are all available in `dx.templates` package.

## Predefined templates

Here is a full example, specifying the `FlatDiv` (default) template.  The following examples will only contain code for the template declaration line.

[demos/cleanup_label_templates.py](./demos/cleanup_label_templates.py)

```python
import dash
import dash_express as dx
import numpy as np
import plotly.express as px

app = dash.Dash(__name__, plugins=[dx.Plugin()])

template = dx.templates.FlatDiv()


@app.callback(
    inputs=dict(
        figure_title=dx.arg("Initial Title", label="Function"),
        fun=dx.arg(["sin", "cos", "exp"], label="Figure Title"),
        phase=dx.arg((1, 10), label="Phase"),
        amplitude=dx.arg((1, 10), label="Amplitude"),
    ),
    template=template,
)
def callback(fun, figure_title, phase, amplitude):
    xs = np.linspace(-10, 10, 100)
    np_fn = getattr(np, fun)

    # Let parameterize infer output component
    x = xs
    y = np_fn(xs + phase) * amplitude
    return template.Graph(
        figure=px.line(x=x, y=y).update_layout(title_text=figure_title)
    )


app.layout = callback.layout(app)

if __name__ == "__main__":
    app.run_server(debug=True)

```

### FlatDiv

The `FlatDiv` template arranges all the input and output containers as children of a top-level `Div` component, and makes no attempt to make the result look nice.

```python=
template = dx.templates.FlatDiv()
```

![](https://i.imgur.com/YSELvgg.png)

### DccCard

The `DccCard` template has no external dependencies and uses some basic inline CSS to place the input and output in a card with a title on top.  It currently puts very little effort into making the result look nice (although this could change).

```python=
template = dx.templates.DccCard(title="Dash Express App", width="500px")
```

![](https://i.imgur.com/387ygkJ.png)

### DbcCard

The `DbcCard` template introduces a dependency on the open source Dash Bootstrap Components library (https://dash-bootstrap-components.opensource.faculty.ai/).  It places all contents in a single bootstrap card, with a card title.

```python=
template = dx.templates.DbcCard(title="Dash Express App", columns=6)
```

![](https://i.imgur.com/q6k008w.png)

### DbcRow

The `DbcRow` template places the inputs and outputs in separate cards and then arranges them in a Bootstrap row. This template is a great choice when integrating the components generated by `@app.callback` into a larger app made with Dash Bootstrap Components.

```python=
template = dx.templates.DbcRow(title="Dash Express App")
```

![](https://i.imgur.com/sLaDDdS.png)

### DbcSidebar

The `DbcSidebar` template creates an app title bar and then includes the inputs in a sidebar on the left of the app, and the outputs in a card in the main app area.  This template is a great choice when using `@app.callback` to build an entire app.

```python=
template = dx.templates.DbcSidebar(title="Dash Express App")
```

![](https://i.imgur.com/wqeZY0B.png)

### DdkCard

The `DdkCard` template introduces a dependency on the proprietary Dash Design Kit library that is included with Dash Enterprise.  Like `DbcCard`, in places all the outputs and inputs in a single card, along with a card title.

```python=
template = dx.templates.DdkCard(title="Dash Express App", width=50)
```

![](https://i.imgur.com/kmX6fuP.png)

### DdkRow

Like the `DbcRow` template, `DdkRow` places the input and output components in separate cards, and then places those cards in a ddk row container.


```python=
template = dx.templates.DdkRow(title="Dash Express App")
```

![](https://i.imgur.com/s29txGA.png)

### DdkSidebar

The `DdkSidebar` template creates a full app experience with an app header, a sidebar for the input controls, and a large main area for the output components.

```python=
template = dx.templates.DdkSidebar(title="Dash Express App")
```

![](https://i.imgur.com/db8a8eo.png)

### Themed DbcSidebar

All of the `Dbc*` components can be themed using the Bootstrap themeing system. Simply pass the URL of a bootstrap theme css file as the `theme` argument of the template. Check out https://www.bootstrapcdn.com/bootswatch/ to browse available templates.

```python=
template = dx.templates.DbcSidebar(
    title="Dash Express App", 
    theme="https://stackpath.bootstrapcdn.com/bootswatch/4.5.2/cyborg/bootstrap.min.css"
)
```

![](https://i.imgur.com/aKy415h.png)

### Themed DdkSidebar

Custom DDK themes created by hand, or using the DDK editor can be passed as the `theme` argument to any of the `Ddk*` templates.

Theme in [demos/ddk_theme.py](./demos/ddk_theme.py)

```python=
from my_theme import theme
template = dx.templates.DdkSidebar(title="Dash Express App", theme=theme)
```

![](https://i.imgur.com/pcmRf1k.png)

## Template component helpers

To make it easier to write code that works well across templates, the template classes provide a few common component constructors like `template.Dropdown` and `template.Graph`.  These can be used in place of the `dcc`, `dbc`, `ddk` variants, and will dispatch to the best component type for the current template.

For example, note that the callback function defined in the `FlatDiv` template example above creates the returned `Graph` using `template.Graph`. In this case, the `Dcc*` and `Dbc*` templates will return a `dcc.Graph`, while the `Ddk*` templates will return a `ddk.Graph`.

These component helpers are also useful when providing explicit components as `@app.callback` arguments. E.g. using `template.Dropdown` will create a `dcc.Dropdown` component for the `Dcc*` and `Ddk*` templates, but a `dbc.Select` component for the `Dbc*` templates.

## Adding additional components to Templates

Callers are free to add additional components to the template before or after passing the template to the `@app.callback` decorator.  The Templates API provides a `add_component` method that can be used to add an arbitrary component to the template, in either the input or output role (or additional custom roles supported by the current template).

The `before` and `after` arguments can be used to position components within the input/output lists generated by `@app.callback`. If the argument values are string, then they refer to the input/output callback function argument names. If the argument values are integers, then they refer to 0-based indices among the components in the specified role.

Here is an example that adds Markdown documentation in between various components generated by `@app.callback`, as well as a `dcc.Link` at the bottom of the page.

[demos/template_with_custom_additions.py](./demos/template_with_custom_additions.py)

```python
import dash
import dash_express as dx
import numpy as np
import dash_core_components as dcc
import plotly.express as px
from ddk_theme import theme

app = dash.Dash(__name__, plugins=[dx.Plugin()])
template = dx.templates.DbcSidebar(title="Dash Express App")

# import dash_core_components as dcc
@app.callback(
    inputs=dict(
        fun=dx.arg(["sin", "cos", "exp"], label="Function"),
        figure_title=dx.arg("Initial Title", label="Figure Title"),
        phase=dx.arg((1, 10), label="Phase"),
        amplitude=dx.arg((1, 10), label="Amplitude")
    ),
    template=template,
)
def function_browser(fun, figure_title, phase, amplitude):
    xs = np.linspace(-10, 10, 100)
    return template.Graph(figure=px.line(
        x=xs, y=getattr(np, fun)(xs + phase) * amplitude
    ).update_layout(title_text=figure_title))


# Add extra component to template
template.add_component(
    template.Markdown("# First Group"),
    role="input", before="fun"
)

template.add_component(
    template.Markdown([
        "# Second Group\n"
        "Specify the Phase and Amplitudue for the chosen function"
    ]),
    role="input", before="phase")

template.add_component(
    template.Markdown([
        "# H2 Title\n",
        "Here is the *main* plot"
    ]),
    role="output", before=0)

template.add_component(
    dcc.Link("Made with Dash", href="https://dash.plotly.com/"),
    role="output", value_property="children"
)

app.layout = function_browser.layout(app)

if __name__ == "__main__":
    app.run_server(debug=True)
```

![](https://i.imgur.com/VX6E6kD.png)

## Creating custom templates
Custom templates can be created by subclassing the `dx.template.base.BaseTemplate` class. Or, for a custom Bootstrap Components template, subclass `dash.teamplates.dbc.BaseDbcTemplate`. Similarly, to create a custom DDK template, subclass `dx.templates.ddk.BaseDdkTemplate`.

Overriding a template may involve:
 1. Customizing what component class is meant by "Dropdown", "Graph", etc.
 2. Specifying the representation of component labels.
 3. How component and label are group together into a container.
 4. How the input and output containers created in (3) are combined into a single layout container.
 5. Providing custom inline CSS which gets inserted into `index.html`.
 6. Customize input and output component inference.

# Chapter 3: A more flexible @app.callback
For the next chapter of this proposal, we'll discuss how the Dash Express `@app.callback` can be thought of as a more flexible version of the Dash 1 `@app.callback`.

The core capability that makes this possible is that the traditional `Input`/`Output`/`State` dependency values can still be provided to `@app.callback` anywhere a component pattern, literal component, or `dx.arg` instance is accepted.  When this is the case, `@app.callback` uses the dependency value for callback registration, but it doesn't create any components or labels for it.

Just like with the Dash 1 `@app.callback`, when a caller provides these dependency values, they are responsible to create and add components with corresponding id's to the app's layout.

## Compatibility with `@app.callback`
The Dash Express `@app.callback` decorator has a superset of the functionality of the Dash 1 `@app.callback` and is fully backward compatible.

## Limitations
In Dash 1, `dash.dependency` objects can be provided to `@app.callback` in several ways.

  1. As positional arguments, or grouped into lists as positional arguments. In this case, `@app.callback` uses the dependency class type (`Input`, `Output`, or `State`) to determine whether to treat the corresponding component+property combination as input, output, or state.

```python=
@app.callback(Output(...), Output(...), [Input(...), Input(...), Input(...)], State(...))
```     

  2. As lists passed to the `output`, `inputs`, or `state` keyword arguments.

```python=
@app.callback(
    output=[Output(...), Output(...)],
    inputs=[Input(...)],
    state=[State(...)]
)
```

When using only `dash.dependency` objects, both forms are supported in Dash Express exactly the same way as Dash 1. However, when using component patterns, literal components, or `dx.arg` values only the second form is supported.

The rest of this chapter describes the new features that are available when using the `output`, `input`, and `state` keyword arguments. 

## Positional or Keyword arguments
In addition to specifying `Input` and `State` values as lists with positional indexes matching the positional indexes of the decorated function, `@app.callback` now also accepts dictionaries to support matching function arguments by keyword.

In this example, the names of the `a`, `b`, and `c` function arguments are significant, rather than their ordering:

```python
@app.callback( 
    output=[Output(...), Output(...)],
    inputs=dict(
        a=Input(...), b=Input(...)
    ),
    state=dict(c=State(...))
)
def param_fn(b, c, a):
    return [a + b, b + c]
```

Note that if `inputs` and `state` are both provided, they must either both be lists, or both be dictionaries.

See `dash-core` issue https://github.com/plotly/dash-core/issues/308

## Tuple and Dictionary argument grouping
The Dash Express `@app.callback` makes it possible to map multiple `Input`/`State` dependency values to a single function argument. As we'll see in Chapter 4, this opens up powerful component+behavior encapsulation workflows.

In other contexts, unpacking composite values like this is sometimes referred to as destructuring

### Tuple grouping
Dependency values can be grouped in a tuple. Here the `ab` function argument is a tuple consisting of the values of two `Input` dependency values

```python
@app.callback(
    output=[Output(...), Output(...)],
    inputs=dict(
        ab=(Input(...), Input(...)),
        c=Input(...)
)
def param_fn(ab, c):
    a, b = ab
    return [a + b, b + c]
```

Or with positional indexing

```python
@app.callback(
    output=[Output(...), Output(...)],
    inputs=[(Input(...), Input(...)), Input(...)]
)
def param_fn(ab, c):
    a, b = ab
    return [a + b, b + c]
```

### Dictionary grouping

Similarly, multiple `Input`/`State` values can be grouped together into a dictionary of values when passed to the function. Here, the `ab` argument will be passed to the function as a dict containing `"a"` and `"b"` keys with values corresponding to the `Input` dependency values in the `@app.callback` specification.

```python
@app.callback(
    output=[Output(...), Output(...)],
    inputs=dict(
        ab=dict(a=Input(...), b=Input(...)),
        c=Input(...)
    )
)
def param_fn(ab, c):
    a, b = ab["a"], ab["b"]
    return [a + b, b + c]
```

It's also possible to nest these groupings arbitrarily deep.

```python
@app.callback(
    output=[Output(...), Output(...)],
    inputs=dict(
        abc=dict(a=Input(...), b=(Input(...), Input(...)))
    )
)
def param_fn(abc):
    a, (b, c) = abc["a"], abc["b"]
    return [a + b, b + c]
```

### Output grouping
The same tuple and dict groupings can be used for the function output values as well

**Output tuple grouping**
```python
@app.callback(
    output=[Output(...), (Output(...), Output(...))],
    inputs=dict(
        a=Input(...), 
        b=Input(...),
        c=Input(...),
    )
)
def param_fn(a, b, c):
    return [a, (a + b, b + c)]
```

**Output dict grouping**
```python
@app.callback(
    output=dict(x=Output(...), y=Output(...)),
    inputs=dict(
        a=Input(...), 
        b=Input(...),
        c=Input(...),
    )
)
def param_fn(a, b, c):
    return dict(x=a+b, y=b+c)
```

# Chapter 4: The CallbackPlugin pattern

## Combining component creation and dependency specification

Some interesting workflows are enabled by the ability to combine component creation, traditional `Input`/`State`/`Output` dependency specifications, and dependency grouping / destructuring.

Here is an example of a callback function that outputs a `go.Figure` and a `pd.DataFrame`, which are displayed in `dcc.Graph` and `DataTable` components, and inputs the `selectedData` prop of the resulting graph.

When a selection is active, the resulting DataFrame is filtered to only include the selected points.

Note that to use a created component as both input and output, the same `id` must be assigned to both the component and the `Input`/`Output` dependency.

[demos/filter_table.py](./demos/filter_table.py)

```python
import dash
import dash_express as dx
import plotly.express as px
from dash.dependencies import Input
import dash_core_components as dcc

tips = px.data.tips()

app = dash.Dash(__name__, plugins=[dx.Plugin()])
graph_id = dx.build_id("graph")
template = dx.templates.DbcCard(title="Scatter Selection")

@app.callback(
    inputs=dict(
        selectedData=Input(graph_id, "selectedData"),
    ),
    output=[
        dx.arg(dcc.Graph(id=graph_id), props="figure"),
        dx.arg(template.DataTable(
            columns=[{"name": i, "id": i} for i in tips.columns],
            page_size=10,
        ), props="data")
    ],
    template=template,
)
def filter_table(selectedData):
    # Let parameterize infer output component
    if selectedData:
        inds = [p["pointIndex"] for p in selectedData["points"]]
        filtered = tips.iloc[inds]
    else:
        filtered = tips
        inds = None

    figure = px.scatter(
        tips, x="total_bill", y="tip"
    ).update_traces(
        type="scatter", selectedpoints=inds
    ).update_layout(dragmode="select")

    return [
        figure,
        filtered.to_dict('records'),
    ]


app.layout = filter_table.layout(app)

if __name__ == "__main__":
    app.run_server(debug=True)
```

![](https://i.imgur.com/bz7oi9l.gif)

## Interactive component builders
Combining component creation and dependency values with the argument grouping features enables a new design pattern for creating components with predefined interactive behavior.  Some examples:

  - table generation with pre-defined Python paging / filtering / sorting / cell styling.
  - plotly-express with datashader updates
  - plotly-express with serverside "animation_frame" sliders
  - plotly-express creating table linked with plot, filtering on selection and highlighting on click
  - Figures with linked axes

### The CallbackPlugin pattern
Here is a proposed architecture that can be used to extract component creation and behavior into a separate class.  The `CallbackPlugin` class encapsulates the creation of inputs, output, and building (output value creation) functionality.

```python
class CallbackPlugin:
    def __init__(config, ...):
        pass

    @property
    def inputs(self):
        raise NotImplementedError

    @property
    def output(self):
        raise NotImplementedError

    @property
    def build(self, inputs_value, **kwargs):
        raise NotImplementedError
```

To make use of a `CallbackPlugin` subclass, users would need to be trained to use the following pattern:

```python
...

plugin = FancyPlugin(**plugin_config)

@app.callback(
    inputs={
        input1=...,
        input2=...,
        plugin_values=plugin.inputs
    },
    outputs=[output1, plugin.output]
)
def hello_plugin(input1, input2, plugin_values):
    # Do stuff with input1 and inputs2 to build result1 and, optionally,
    # build_config
    return result1, plugin.build(plugin_values, **build_config)
    
...
```

The component creation capabilities of `@app.callback` allow plugins to define their own input and output components, as well as define dependencies to make it possible to both input and output properties of the same component.  Following this pattern, the plugins do not need to define their own callbacks, making it much easier to compose plugins and connect them with custom functionality.

The tuple/dict grouping feature of `@app.callback` allow plugins to store any number of input and output components and make them look like a single value to the user. e.g. `plugin.inputs` and `plugin_values` above can be dictionaries with any number of keys, but the user can treat them as a single scalar value, so that they can always follow the same usage pattern.

Here is a plugin implementation of the scatter+table implemented manually above. This is what would go in a reusable library.

[demos/filter_table_plugin.py](./demos/filter_table_plugin.py)

```python
from dash.dependencies import Input
import dash_express as dx
import plotly.express as px
from dash_express import ComponentPlugin


class FilterTable(ComponentPlugin):
    def __init__(self, df, px_kwargs=None, page_size=5, template=None):
        if px_kwargs is None:
            px_kwargs = dict(x=df.columns[0], y=df.columns[1])

        if template is None:
            template = dx.templates.FlatDiv()

        self.df = df
        self.px_kwargs = px_kwargs
        self.page_size = page_size
        self.template = template
        self._compute_props(template)

    def _compute_props(self, template):
        self.graph_id = dx.build_id(name="filter-table-graph")
        self.datatable_id = dx.build_id(name="filter-table-table")
        self._output = [
            dx.arg(template.Graph(id=self.graph_id), props="figure"),
            dx.arg(template.DataTable(
                id=self.datatable_id,
                columns=[{"name": i, "id": i} for i in self.df.columns],
                page_size=self.page_size
            ), props="data"),
        ]

        self._inputs = Input(self.graph_id, "selectedData")

    def _build(self, inputs_value, df=None):
        if df is None:
            df = self.df

        inds = self.selection_indices(inputs_value)
        if inds:
            filtered = df.iloc[inds]
        else:
            filtered = df

        figure = px.scatter(
            df, **self.px_kwargs
        ).update_traces(
            type="scatter", selectedpoints=inds
        ).update_layout(dragmode="select")

        return [figure, filtered.to_dict("records")]

    def selection_indices(self, inputs_value):
        selectedData = inputs_value
        if selectedData:
            inds = [p["pointIndex"] for p in selectedData["points"]]
        else:
            inds = None

        return inds

    @property
    def inputs(self):
        return self._inputs

    @property
    def output(self):
        return self._output

    def build(self, inputs_value, df=None):
        if df is None:
            df = self.df
        return self._build(inputs_value, df)
```

And here is how the plugin can be incorporated into a `@app.callback` app. This is what a user would hand-code in their app.

[demos/filter_table_with_plugin.py](./demos/filter_table_with_plugin.py)

```python
import dash
import dash_express as dx
import plotly.express as px
from filter_table_plugin import FilterTable

template = dx.templates.DbcCard(title="Scatter Selection")

tips = px.data.tips()
filter_table_plugin = FilterTable(
    tips, px_kwargs=dict(x="total_bill", y="tip"), page_size=12, template=template
)

app = dash.Dash(__name__, plugins=[dx.Plugin()])

@app.callback(
    template=template,
    inputs=[filter_table_plugin.inputs],
    output=filter_table_plugin.output,
)
def filter_table(inputs_value):
    print(filter_table_plugin.selection_indices(inputs_value))
    return filter_table_plugin.build(inputs_value)


app.layout = filter_table.layout(app)

if __name__ == "__main__":
    app.run_server(debug=True)
```

Notice that `output` and `build` in the plugin return tuples. This makes it possible for the user to position all the inputs and outputs as single values in the `@app.callback` decorator, and in the wrapped function signature.  This makes it straightforward for a single call to `@app.callback` to use multiple plugins in the same function. Additionally, plugins could provide additional utility methods to expose extra info to the user inside a callback, like the list of selected indices in this case.

With a bit more work in the `FilterTable` plugin, options to perform serverside paging and sorting, conditional formatting, clientside or serverside filtering, etc. could be added without changing anything for the user other than adding more configuration options to the constructor.
