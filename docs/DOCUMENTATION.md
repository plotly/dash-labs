# Overview
Dash Express is a project to significantly expand the capabilities of the Dash `@app.callback` decorator. This project is beginning its life as a separate package that depends on Dash, but the goal is that the successful ideas from this project will migrate into Dash as part of Dash 2.0.

## Design Goals
Dash Express began with several interdependent design goals:
 - Provide a more concise syntax for generating simple Dash apps that follow a variety of nice looking predefined templates.
 - Make it possible for third-party developers to develop and distribute custom templates
 - Ensure that there is a smooth continuum between concision, and the flexibility of "full Dash". The concise syntax should not be a dead-end, requiring the developer to rewrite the app in order to reach a certain level of sophistication.
 - Improve ability of users to encapsulate and reuse custom interactive component workflows, and make it possible for third-party developers to distribute these as plugins.


# Design
The Dash Express design centers on the `@dx.callback` decorator.

> it is recommended to import `dash_express` as `dx`, and this is the convention that will be used throughout this document.
 
As described below, this decorator retains all of the functionality of the existing (Dash 1) `@app.callback` decorator, but it also includes the ability to optionally generate components and lay them out according to predefined templates.

The capabilities of the `@dx.callback` decorator can be approached from two sides. First, as a Dash implementation of the ipywidgets [`@interact`](https://ipywidgets.readthedocs.io/en/stable/examples/Using%20Interact.html) feature. Second, as a more flexible extension of the Dash 1 `@app.callback` feature set.  This document will start with the former (Chapters 1 and 2), and then discuss the latter (Chapter 3).

# Chapter 1: @interact-style app generation
Dash Express makes it possible to generate simple apps directly from the `@dx.callback` decorator using a style that is inspired by (though not syntactically compatible with) the [`@interact`](https://ipywidgets.readthedocs.io/en/stable/examples/Using%20Interact.html) decorator.

## Basic Example
In this first example, the `greet` function inputs 4 arguments and outputs a `dcc.Graph` component. The graph's figure is configured by these 4 inputs.  By passing component patterns (called [widget abbreviations](https://ipywidgets.readthedocs.io/en/stable/examples/Using%20Interact.html#Widget-abbreviations) in the ipywidgets documentation), the `@dx.callback` decorator is told to construct appropriate Dash components for each input argument.  Supported patterns include:

 - Lists (either lists of strings, or lists of dicts with `value` and `label` keys) are converted to dropdowns
 - Tuples are converted to sliders. First and second value are the min and max. An optional third value is the step size
 - Strings are converted to `Input` boxes
 - Booleans are converted to checkboxes.

> Note: Other patterns are under consideration (e.g. datetime values to date pickers, and DataFrame's to DataTables), but these are more complex because they would require a preprocessing step to convert the raw Dash component values to specialized Python data structures when calling the callback function.

As mentioned below, the set of available patterns can be extended by the current `Template`.

[docs/demos/basic_decorator.py](docs/demos/basic_decorator.py)
```python
import dash
import dash_express as dx
import numpy as np
import dash_core_components as dcc
import plotly.express as px

app = dash.Dash(__name__)


@dx.callback(
    app,
    inputs=dict(
        fun=["sin", "cos", "exp"],
        figure_title="Initial Title",
        phase=(1, 10),
        amplitude=(1, 10),
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

The `@dx.callback` decorator now returns a class called a `CallbackWrapper`.  This will be covered in more depth later, but the simplest role of this class is to provide a `.layout(app)` method that generates a top-level Dash component that contains all of the generated components, and that is suitable for assignment directly to the `app.layout` property.  This method also configures all of the callbacks necessary to produce the interactive app.  Here's what the end result looks like in this case. 

![](https://i.imgur.com/Kl9Walj.gif)

> **Note:** Since no template was specified, the default `FlatDiv` template was used. This template simply places all of the components, inputs followed by outputs, in a flat `Div` element.  Much better looking templates will be introduced in Chapter 2.

## Customizing labels
As seen above, `@dx.callback` automatically generates a label for each component it creates.  These labels default to the parameter names when the `inputs` argument is a dictionary, and they default to the positional index of the argument if `inputs` is specified as a list (more on `inputs` as lists in [Chapter 3](#Chapter-3-A-more-flexible-appcallback)).

These labels can be customized by wrapping the input pattern with `dx.arg` and overriding the `label` keyword argument. The following example assigns custom labels to all of the inputs.

[demos/basic_decorator_labels.py](./demos/basic_decorator_labels.py)

```python
import dash
import dash_express as dx
import numpy as np
import dash_core_components as dcc
import plotly.express as px

app = dash.Dash(__name__)

@dx.callback(
    app,
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

The parameter pattern grammar is convenient, but it's also pretty limited, both in term of the number of available components and the component styling. To provide the next level of customization, User-defined components can be provided as well.

This example specifies component instances for the `figure_title` and `phase` with customized styling and default values. It also introduces a new `date` parameter that is concatenated with the title on the figure.

 - `figure_title` is now represented by an `dcc.Input` with a crimson background and white text
 - `phase` is now a dropdown of numbers instead of a slider. This also makes it possible to specify a default value of 4
 - `date` is a `dcc.DatePickerSingle` component which provides the callback function with a date string.

Notice that the `DatePickerSingle` value is specified using a new syntax: `DatePickerSingle().props["date"]`. This expression returns an instance of a new `dx.ComponentProps` class. This class maintains a reference to both a component, and one or more properties of that component. Providing `@dx.callback` with a `ComponentProps` value makes it possible to specify which property (or properties) of the component is used as input for the decorated callback function.  For convenience, the default property is "value", which is why the `component.props[...]` syntax is not required for the `Input` and `Select` components.

[demos/specialize_components.py](./demos/specialize_components.py)

```python
import dash
import dash_express as dx
import numpy as np
import dash_core_components as dcc
import dash_bootstrap_components as dbc
import plotly.express as px

app = dash.Dash(__name__)

@dx.callback(
    app,
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
        date=dx.arg(dcc.DatePickerSingle().props["date"], label="Measurement Date")
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
Some components have multiple properties that could be considered the "value" of the component for the purpose of decorated function. One common example is the `DatePickerRange` component.  For this component, the start date is stored in the `start_date` prop and the end date in the `end_date` prop.  To make it possible to pass both of these values to the function, the argument to the `component.props[...]` expression may be a tuple (or dict) of multiple properties.

In this example, a tuple of `("start_date", "end_date")` is specified, which results in a tuple of the corresponding component property values to be passed to the decorated callback function. 

[demos/multi_input_component.py](./demos/multi_input_component.py)

```python
import dash
import dash_express as dx
import plotly.graph_objects as go
import dash_core_components as dcc

app = dash.Dash(__name__)


@dx.callback(
    app,
    inputs=dict(
        figure_title=dx.arg("Initial Title", label="Graph Title"),
        date_range=dx.arg(
            dcc.DatePickerRange().props[("start_date", "end_date")], label="Date"
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

The ipywidgets `@interact` decorator supports a `manual` argument. When `True`, an update button is automatically added and changes to the other widgets are not applied until the update button is clicked.  This workflow can be replicated with `@dx.callback` by adding an `html.Button` component and specifying that all inputs other than the button should be classified as `State` (rather than the default of `Input`).  Whether an input is considered `Input`, `State`, or `Output` can be overridded using the `kind` argument to the `dx.arg` wrapper.

Here is a full example

[demos/basic_decorator_labels_state.py](./demos/basic_decorator_labels_state.py)

```python
import dash
import dash_express as dx
import numpy as np
import dash_core_components as dcc
import dash_html_components as html
import plotly.express as px

app = dash.Dash(__name__)

@dx.callback(
    app,
    inputs=dict(
        fun=dx.arg(["sin", "cos", "exp"], label="Function", kind="state"),
        figure_title=dx.arg("Initial Title", label="Figure Title", kind="state"),
        phase=dx.arg((1, 10), label="Phase", kind="state"),
        amplitude=dx.arg((1, 10), label="Amplitude", kind="state"),
        n_clicks=dx.arg(html.Button("Update").props["n_clicks"], kind="input")
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
The `@dx.callback` decorator no longer requires a caller to explicitly provide the output component that the callback function result will be stored in. The default behavior is the create an output `html.Div` component and to store all of the function results as the `children` property of this `Div`.  However, explicit output components and output props can also be configured using the `output` argument to `@dx.callback`.

Here is an example that outputs a string to the `children` property of a `dcc.Markdown` component.


[demos/output_markdown.py](./demos/output_markdown.py)

```python
import dash
import dash_core_components as dcc
import dash_express as dx

app = dash.Dash(__name__)

@dx.callback(
    app,
    inputs={
        "input_text": dx.arg(
            dcc.Textarea(value="## Heading\n"), label="Enter Markdown"
        )
    },
    output=dcc.Markdown().props["children"],
)
def markdown_preview(input_text):
    return input_text


app.layout = markdown_preview.layout(app)

if __name__ == "__main__":
    app.run_server(debug=True)
```

![](https://i.imgur.com/9PEuHcg.gif)

## Output component inference

For the special case of values being output as the `children` property of an output component (as is the default when `output` is not provided), `@dx.callback` will now perform output component inference.  `@dx.callback` will examine all such returned values, and for those that are not already simple JSON values, it will try to identify an appropriate component with which to display the value. Default inferences include:

 - `go.Figure` to `Graph.figure` (either dcc or ddk depending on the template)
 - `pd.DataFrame` -> `DataTable.data` (either `dash_table` or `ddk` depending on template)

Templates can specify additional output inferences.

## Accessing individual components to build custom layouts

### `CallbackWrapper`
Before discussion of the Template system (Chapter 2), we'll cover how the `@dx.callback` decorator can be used to construct the function input components, and define the callbacks, but still maintain full control over the app layout.

As mentioned briefly above, the type of the value returned by the `@dx.callback` decorator is a `CallbackWrapper` instance. First of all, as expected of a decorator result, this value can be still called just like the function it wraps.  Additionally, it provides the following attributes:

 - `.template`: A template instance that is capable of laying out the input/constructed components. This defaults to the `FlatDiv` template mentioned above that simply adds everything as children of a single top-level `html.Div` component.
 - `.roles`: This is a dictionary from template "roles" to `OrderedDict`s of `ArgumentComponents` (described below). All templates define at least two roles: "input" and "output". By default, all components corresponding to the `@dx.callback` `inputs` and `state` arguments are assigned the "input" role and therefore are included in the `.roles["input"]` `OrderedDict`. Similarly, all components corresponding to the `@dx.callback` `output` argument are assigned the "output" role and therefore are included in the `.roles["output"]` `OrderedDict`.

A `CallbackWrapper` instance also provides the `.layout(app)` method that we've been using so far to ask the template to generate a layout containing all of the callbacks created or provided components.

### ArgumentComponents

You might think that the values of the `.roles["inputs"]` and `.roles["output"]` dictionaries described above would simply be the components that `@dx.callback` created.  The reason it's not quite that simple is that for a single callback function argument, `@dx.callback` may create multiple components: One for the input value and one for the label. And both of these may be wrapped in a container component.  Because the caller may want access to any, or all, of these components individually, references to all of these components are stored in a `ArgumentComponents` instance as `CallbackProps` values.  Here are the properties of `ArgumentComponents`, and an example of why a caller may want to access them.

 - `.value`: This is a `ComponentProp` for the innermost component that actually provides the callback function with an input value. A caller would want to access this component in order to register additional callback functions to execute when the callback function is updated.
 - `.label`: This is the `ComponentProp` for the component that displays the label string for the component. A caller may want to access this component to customize the label styling, or access the current value of the label string.
 - `.container`: This is the `ComponentProp` for the outer-most component that contains all of the other components described above. This is generally the component that a caller should incorporate when building a custom layout.

This example uses `@dx.callback` to create components and install callbacks, constructs a fully custom layout, and defines custom callbacks on the components returned by `@dx.callback`. This is loosely based on the Dash Bootstrap Components example at https://dash-bootstrap-components.opensource.faculty.ai/examples/iris/. 

Notice how custom callbacks are applied to the dropdowns returned by `@dx.callback` to prevent specifying the same feature as both x and y values.

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
app = dash.Dash(__name__)


# Use dx.callback to create components
@dx.callback(
    app,
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

# Get the dropdown components that were created by dx.callback
x_component = iris.roles["input"]["x"].value
y_component = iris.roles["input"]["y"].value


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
x_container = iris.roles["input"]["x"].container.component
y_container = iris.roles["input"]["y"].container.component
output_container = iris.roles["output"][0].container.component

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
When an input or output component is generated from a pattern, or a component instance is passed in without an id, `@dx.callback` will create an id of the form `{"uid": "{uuid-value}", "name": "parameter name or index"}`. The inclusion of the UID ensures that component id's won't clash when the results of `@dx.callback` are integrated into a larger app.

 > Note: a fixed random seed is used to ensure that the UUID's generated during app construction are deterministic across app instances

# Chapter 2: Template system
As noted above, the `.layout(app)` method of a `CallbackWrapper` instance builds a Dash component layout that displays all of the generated and provided components.  This layout is customized using templates.

For a caller, specifying a template is simply a matter of proving a template instance as the `template` argument to `@dx.callback`.  Built-in templates are all available in `dx.templates` package.

## Predefined templates

Here is a full example, specifying the `FlatDiv` (default) template.  The following examples will only contain code for the template declaration line.

[demos/cleanup_label_templates.py](./demos/cleanup_label_templates.py)

```python
import dash
import dash_express as dx
import numpy as np
import plotly.express as px

app = dash.Dash(__name__)

template = dx.templates.FlatDiv()

@dx.callback(
    app,
    inputs=dict(
        figure_title=dx.arg("Initial Title", label="Function"),
        fun=dx.arg(["sin", "cos", "exp"], label="Figure Title"),
        phase=dx.arg((1, 10), label="Phase"),
        amplitude=dx.arg((1, 10), label="Amplitude"),
    ),
    template=template,
)
def callback_components(fun, figure_title, phase, amplitude):
    xs = np.linspace(-10, 10, 100)
    np_fn = getattr(np, fun)

    x = xs
    y = np_fn(xs + phase) * amplitude
    return template.Graph(
        figure=px.line(x=x, y=y).update_layout(title_text=figure_title)
    )

app.layout = callback_components.layout(app)

if __name__ == "__main__":
    app.run_server(debug=True)
```

### FlatDiv

The `FlatDiv` template puts all of the input and output containers as children of a top-level `Div` component, and makes no attempt to make the result look nice.

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

The `DbcRow` template places the inputs and outputs in separate cards and then arranges them in a Bootstrap row. This template is a great choice when integrating the components generated by `@dx.callback` into a larger app made with Dash Bootstrap Components.

```python=
template = dx.templates.DbcRow(title="Dash Express App")
```

![](https://i.imgur.com/sLaDDdS.png)

### DbcSidebar

The `DbcSidebar` template creates an app title bar and then includes the inputs in a sidebar on the left of the app, and the outputs in a card in the main app area.  This template is a great choice when using `@dx.callback` to build an entire app.

```python=
template = dx.templates.DbcSidebar(title="Dash Express App")
```

![](https://i.imgur.com/wqeZY0B.png)

### DdkCard

The `DdkCard` template introduces a dependency on the proprietary Dash Design Kit library that is included with Dash Enterprise.  Like `DbcCard`, in places all of the outputs and inputs in a single card, along with a card title.

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

The `DdkSidebar` template creates a full app experience with an app header, a sidebard for the input controls, and a large main area for the output components.

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

To make it easier to write code that works well across templates, the template classes provide a few common component constructors like `template.Dropdown` and `template.Graph`.  These can be used in place of the `dcc`, `dbc`, `ddk` variants, and will dispatch to the best component for the current template.

For example, note that the callback function defined in the `FlatDiv` template example above creates the returned `Graph` using `template.Graph`. The `Dcc*` and `Dbc*` templates will return a `dcc.Graph`, while the `Ddk*` templates will return a `ddk.Graph`.

These component helpers are also useful when providing explicit components as `@dx.callback` values. E.g. using `template.Dropdown` will create a `dcc.Dropdown` component for the `Dcc*` and `Ddk*` templates, but a `dbc.Select` component for the `Dbc*` templates.

## Adding additional components to Templates

Callers are free to add additional components to the template before or after passing the template to the `@dx.callback` decorator.  The Templates API provides a `add_component` method that can be used to add an arbitrary component to the template, in either the input or output role (or custom roles supported by the current template).

The `before` and `after` arguments can be used to position components within the input/output lists generated by `@dx.callback`. If the argument values are string, then they refer to the input/output callback function argument names. If the argument values are integers, then they 0-based indices among the components in the specified role.

Here is an example that adds Markdown documentation to various components generated by `@dx.callback`, as well as a `dcc.Link` at the bottom of the page.

```python
import dash
import dash_express as dx
import numpy as np
import dash_core_components as dcc
import plotly.express as px
from ddk_theme import theme
import dash_html_components as html

app = dash.Dash(__name__)
template = dx.templates.DbcSidebar(title="Dash Express App")

# import dash_core_components as dcc
@dx.callback(
    app,
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

## Creating custom templates
Custom templates can be created by subclassing the `dx.template.base.BaseTemplate` class. Or, for a custom Bootstrap Components template, subclass `dash.teamplates.dbc.BaseDbcTemplate`. Similarly, to create a custom DDK template, subclass `dx.templates.ddk.BaseDdkTemplate`.

Overriding a template may involve:
 1. Customizing what component class is meant by "Dropdown", "Graph", etc.
 2. Specifying the representation of component labels.
 3. How component, label, and optional component are group together into a container.
 4. How the input and output containers created in (4) are combined into a single layout container.
 5. Providing custom inline CSS which gets inserted into `index.html`

# Chapter 3: A more flexible @app.callback
For the next chapter of this proposal, we'll discuss how the Dash Express `@dx.callback` can be thought of as a more flexible version of the Dash 1 `@app.callback`.

The core capability that makes this possible is that the traditional `Input`/`Output`/`State` dependency values can still be provided to `@dx.callback` anywhere a component pattern, or literal component, is accepted.  When this is the case, `@dx.callback` uses the dependency value for callback registration, but it doesn't create any components/labels/checkboxes etc.

Just like with the Dash 1 `@app.callback`, when a caller provides these dependency values, they are responsible to create and add components with corresponding id's to the app's layout.

## Compatibility with `@app.callback`
The Dash Express `@dx.callback` decorator is semantically a superset of the Dash 1 `@app.callback` decorator, and is nearly syntactically compatible. The main difference is that, currently, `@dx.callback` is not a method on the `dash.Dash` app object, and so the app must be passed as the first argument to function.

The exact same result is obtained by decorating it with either of these

```python=
app.callback([Output(...), Output(...)], [Input(...), Input(...)])(fn)
dx.callback(app, [Output(...), Output(...)], [Input(...), Input(...)])(fn)
```

State is similarly supported the same way
```python=
app.callback([Output(...), Output(...)], [Input(...)], [State(...)])(fn)
dx.callback(app, [Output(...), Output(...)], [Input(...)], [State(...)])(fn)
```

And explicit keyword argument names for `inputs`, `output`, and `state` can be used in either case
```python=
app.callback(
    output=[Output(...), Output(...)],
    inputs=[Input(...)],
    state=[State(...)]
)(fn)
```

The `prevent_initial_call` argument is supported just like `dash.Dash.callback`

## Incompatibility
The only current incompatibility of `@dx.callback` compared to Dash 1 `@app.callback` is that each of `inputs`, `outputs`, and `state` values must be provided as a single argument (either a scalar value or a list). So things like this are not currently supported:

```python=
@app.callback(Output(...), Output(...), Input(...), Input(...), Input(...))
```

The inputs and outputs would need to be grouped into lists

```python=
@dx.callback([Output(...), Output(...)], [Input(...), Input(...), Input(...)])
```

It should be possible to support this syntax for backward compatibility, but it probably won't be possible to support mixing dependency and component instances this way.

## Positional or Keyword arguments
In addition to specifying `Input` and `State` values as lists with positional indexes matching the positional indexes of the decorated function, `@dx.callback` also accepts dictionaries to support matching function arguments by keyword.

In this example, the names of the `a`, `b`, and `c` function arguments are significant, rather than their ordering:

```python
@dx.callback(
    app, 
    output=[Output(...), Output(...)],
    inputs=dict(
        a=Input(...), b=Input(...)
    ),
    state=dict(c=State(...))
)
def param_fn(a, b, c):
    return [a + b, b + c]
```

Note that if `inputs` and `state` are both provided, they must either both be lists, or both be dictionaries.

See `dash-core` issue https://github.com/plotly/dash-core/issues/308

## Tuple and Dictionary argument grouping
The Dash Express `@dx.callback` makes it possible to map multiple `Input`/`State` dependency values to a single function argument. As we'll see in Chapter 4, this opens up powerful component+behavior encapsulation workflows.

In other contexts, unpacking composite values like this is sometimes referred to as destructuring

### Tuple grouping
Dependency values can be grouped in a tuple. Here the `ab` argument is a tuple consisting of the values of two `Input` dependency values

```python
@dx.callback(
    app,
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
@dx.callback(
    app,
    output=[Output(...), Output(...)],
    inputs=[(Input(...), Input(...)), Input(...)]
)
def param_fn(ab, c):
    a, b = ab
    return [a + b, b + c]
```

### Dictionary grouping

Similarly, multiple `Input`/`State` values can be grouped together into a dictionary of values when passed to the function. Here, the `ab` argument will be passed to the function as a dict containing `"a"` and `"b"` keys with values corresponding to the `Input` dependency values in the `@dx.callback` specification.

```python
@dx.callback(
    app,
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
@dx.callback(
    app,
    output=[Output(...), Output(...)],
    inputs=dict(
        abc=dict(a=Input(...), b=(Input(...), Input(...)))
    )
)
def param_fn(ab, c):
    a, (b, c) = ab["a"], ab["b"]
    return [a + b, b + c]
```

### Output grouping
The same tuple and dict groupings can be used for the function output values as well

**Output tuple grouping**
```python
@dx.callback(
    app,
    output=(Output(...), Output(...)),
    inputs=dict(
        a=Input(...), 
        b=Input(...),
        c=Input(...),
    )
)
def param_fn(a, b, c):
    return (a + b, b + c)
```

**Output dict grouping**
```python
@dx.callback(
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

app = dash.Dash(__name__)
graph_id = dx.build_id("graph")
template = dx.templates.DbcCard(title="Scatter Selection")


@dx.callback(
    app,
    inputs=dict(
        selectedData=Input(graph_id, "selectedData"),
    ),
    output=[
        dcc.Graph(id=graph_id).props["figure"],
        template.DataTable(
            columns=[{"name": i, "id": i} for i in tips.columns],
            page_size=10,
        ).props["data"]
    ],
    template=template,
)
def filter_table(selectedData):
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
Combining the component creation and dependency values with the argument grouping features enables a new design pattern for creating components with predefined interactive behavior.  Some examples:

  - table generation with pre-defined Python paging / filtering / sorting / cell styling.
  - plotly-express with datashader updates
  - plotly-express with serverside "animation_frame" sliders
  - plotly-express creating table linked with plot, filtering on selection and highlighting on click
  - Figures with linked axes

### The CallbackPlugin pattern
Here is a proposed architecture that can be used to extract component creation and behavior into a separate class.  The `CallbackPlugin` class encapsulates the creation of inputs, output, and building (output value creation) functionality.

```python=
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

@dx.callback(
    app,
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

The component creation capabilities of `@dx.callback` allow plugins to define their own input and output components, as well as define dependencies to make it possible to both input and output properties of the same component.  Following this pattern, the plugins do not need to define their own callbacks, making it much easier to compose plugins and connect them with custom functionality.

The tuple/dict grouping feature of `@dx.callback` allow plugins to store any number of input and output components and make them look like a single value to the user. e.g. `plugin.inputs` and `plugin_values` above can be dictionaries with any number of keys, but the user can treat them as a single scalar value, so that they can always follow the same usage pattern.

Here is a plugin implementation of the scatter+table implemented manually above. This is what would go in a reusable library.

[demos/filter_table_plugin.py](./demos/filter_table_plugin.py)

```python
from dash.dependencies import Input
import dash_express as dx
import plotly.express as px
from dash_express.plugin import ParameterPlugin


class FilterTable(ParameterPlugin):
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
            template.Graph(id=self.graph_id).props["figure"],
            template.DataTable(
                id=self.datatable_id,
                columns=[{"name": i, "id": i} for i in self.df.columns],
                page_size=self.page_size
            ).props["data"],
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

And here is how the plugin can be incorporated into a `@dx.callback` app. This is what a user would hand-code in their app.

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

app = dash.Dash(__name__)

@dx.callback(
    app,
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

Notice that `output` and `build` in the plugin return tuples. This makes it possible for the user to position all of the inputs and outputs as single values in the `@dx.callback` decorator, and in the wrapped function signature.  This makes it straightforward for a single call to `@dx.callback` to use multiple plugins in the same function. Additionally, plugins could provide additional utility methods to expose extra info to the user inside a callback, like the list of selected indices in this case.

With a bit more work in the `FilterTable` plugin, options to perform serverside paging and sorting, conditional formatting, clientside or serverside filtering, etc. could be added without changing anything for the user other than adding more configuration options to the constructor.
