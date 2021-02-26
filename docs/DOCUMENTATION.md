# Overview
Dash Labs is a project to significantly expand the capabilities of Dash. This project is beginning its life as a separate package that depends on Dash, but the goal is that the successful ideas from this project will migrate into future versions of Dash itself.

## Design Goals
Dash Labs began with several interdependent design goals:
 - Provide a more concise syntax for generating simple Dash apps that follow a variety of nice looking predefined templates.
 - Make it possible for third-party developers to develop and distribute custom templates
 - Ensure that there is a smooth continuum between concision, and the flexibility of "full Dash". The concise syntax should not be a dead-end, requiring the developer to rewrite the app in order to reach a certain level of sophistication.
 - Improve ability of users to encapsulate and reuse custom interactive component workflows, and make it possible for third-party developers to distribute these as plugins.


# Design
The Dash Labs design centers on enhancements to the `@app.callback` decorator, enabled through the application of the `dl.Plugin()` Dash plugin.

> it is recommended to import `dash_express` as `dx`, and this is the convention that will be used throughout this document.
 
This document will start with the Dash 1 feature set, and then progressively describe the extensions provided by Dash Labs.  This is how an experienced Dash 1 user might learn about Dash Labs. An alternative introduction should later be developed for new users learning Dash for the first time in the context of Dash Labs. 

This document is organized into the following chapters:
 - Chapter 1: A more flexible `@app.callback`:
    - Named argument support
    - Argument grouping     
    - Interleaveable `Input` and `State` arguments
    - Ability to provide components instead of id's

 - Chapter 2: The template layout system
    - Ability to automatically arrange components passed to `@app.callback` using a predefined template
    
 - Chapter 3: Template component constructors
    - Concise convenience functions for building component dependencies to pass to app.callback

 - Chapter 4: More examples

 - Chapter 5: The Component Plugin design pattern
    - Design pattern that can be used to bundle components and behavior into reusable plugins


# Chapter 1: A more flexible `@app.callback`
This chapter covers the core enhancements to `@app.callback` that are introduced by Dash Labs.

## Enabling the Dash Labs plugin
The Dash Labs features are enabled by specifying an instance of dx.Plugin when instantiating a Dash app.

```python
import dash
import dash_labs as dx

app = dash.Dash(__name__, plugins=[dx.Plugin()])
```

## Positional or Keyword arguments
In Dash 1, the `Input`/`State`/`Output` dependency objects are always provided to `@app.callback` as positional arguments (either positional arguments directly to `@app.callback`, or as lists to the `inputs`/`state`/`output` keyword arguments).  The order in which the dependency objects are provided dictates the order of the positional arguments that are passed to the decorated callback function.  This means that the names of the callback function arguments don't matter, only the order they are defined in.

### Positional arguments
Here are a few examples of positional dependency specification in Dash 1:
```python
@app.callback( 
    Output(...), Output(...),
    Input(...), Input(...),
    State(...)
)
def callback(a, b, c):
    return [a + b, b + c]
```

```python
@app.callback( 
    [Output(...), Output(...)],
    [Input(...), Input(...)],
    [State(...)]
)
def callback(a, b, c):
    return [a + b, b + c]
```

```python
@app.callback( 
    output=[Output(...), Output(...)],
    inputs=[Input(...), Input(...)],
    state=[State(...)]
)
def callback(a, b, c):
    return [a + b, b + c]
```

### Keyword arguments
In Dash Labs, callback functions can register to be called with named keyword arguments.  This is done by passing dictionaries to the `inputs` and `state` arguments of `@app.callback`. In this case, the order of the callback's function arguments doesn't matter. All that matters is that the keys of the dependency dictionary match the function argument names.

Here is an example of using keyword input and state arguments:

```python
@app.callback( 
    output=[Output(...), Output(...)],
    inputs=dict(a=Input(...), b=Input(...)),
    state=dict(c=State(...))
)
def callback(b, c, a):
    return [a + b, b + c]
```

Here the order of the callback function arguments doesn't matter, only the names.

The output of a callback function can also be specified using named arguments. In this case the function is expected to return a dictionary with keys matching the keys in the dictionary passed to the `output` argument of `@app.callback`.  For example:

```python
@app.callback( 
    output=dict(x=Output(...), y=Output(...)),
    inputs=dict(a=Input(...), b=Input(...)),
    state=dict(c=State(...))
)
def callback(b, c, a):
    return dict(x=a + b, y=b + c)
```

## Interchangeable Input and State
Because it is never ambiguous, Dash Labs supports freely mixing `Input` and `State` dependencies objects. This means that `State` dependencies can be included in the `inputs` argument, and `Input` dependencies can be included in the `state` argument.  To simplify things going forward, a new `args` keyword argument has been added that may contain a mix of `Input` and `State` dependencies. The recommended style going forward is to put both `Input` and `State` dependencies in `args` rather than using both `inputs` and `state`.

For example:

```python
@app.callback( 
    output=dict(x=Output(...), y=Output(...)),
    args=dict(a=Input(...), b=Input(...), c=State(...)),
)
def callback(b, c, a):
    return dict(x=a + b, y=b + c)
```

## Tuple and Dictionary argument grouping
The Dash Labs `@app.callback` makes it possible to combine multiple `Input`/`State` dependency values to a single function argument. As we'll see in Chapter 5, this opens up powerful component+behavior encapsulation workflows.

In other contexts, unpacking grouped values like this is sometimes referred to as destructuring.

### Tuple grouping
Dependency values can be grouped in a tuple. Here the `ab` keyword function argument is a tuple consisting of the values of two `Input` dependency values

```python
@app.callback(
    output=[Output(...), Output(...)],
    args=dict(
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
    args=[(Input(...), Input(...)), Input(...)]
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
    args=dict(
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
    args=dict(
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
    args=dict(
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
    output=[Output(...), dict(x=Output(...), y=Output(...))],
    inputs=dict(
        a=Input(...), 
        b=Input(...),
        c=Input(...),
    )
)
def param_fn(a, b, c):
    return [a, dict(x=a+b, y=b+c)]
```

## Support for passing components in place of id's
dash-labs makes it possible to include a component instance in place of a component id in the `Input`, `State`, and `Output` dependency objects.  This feature is currently provided by the special `dx.Input`, `dx.State`, `dx.Output` classes. Dash Labs apps should use these classes in place of the Dash 1 `dash.dependency.Input`, `State`, and `Output` classes.  

```python
div = html.Div()
button = html.Button(children="Click Me")

@app.callback(Output(div, "children"), Input(button, "n_clicks"))
def callback(n_clicks):
    return "Clicked {} times".format(n_clicks)

# Include div and button in app.layout below
```

When a dependency wraps a component, the `component_property` specification in the dependency object can be a single property as a string (as in Dash 1), or it can be a tuple or dictionary grouping of multiple properties of the component.  Here is an example with the `DatePickerRange` component:

```python
div = html.Div()
date_picker_range = dcc.DatePickerRange()
@app.callback(Output(div, "children"), Input(date_picker_range, ("start_date", "end_date")))
def callback(date_range):
    start_date, end_date = date_range
    return f"Start date: {}\n End date: {}".format(start_date, end_date)
```

## Component id's
If a component does not have an id when it is wrapped in a dependency, a unique id is created and assigned to the component automatically. These unique IDs are generated deterministically (no randomly) in order to be consistent across processes.

# Chapter 2: The template layout system
Dash Labs introduces a template system that makes it possible to quickly add components to a pre-defined template.  As will be described below, the template system integrates with `@app.callback`, but templates can also be used independently of `@app.callback`.

Templates that are included with Dash Labs are located in the `dx.templates` package.  The convention is to assign a template instance to a variable named `tpl`. Components can then be added to the template with `tpl.add_component` 

[demos/template_system1.py](demos/template_system1.py)

```python
import dash_labs as dx
import dash_html_components as html
import dash

app = dash.Dash(__name__, plugins=[dx.Plugin()])
tpl = dx.templates.DbcCard(title="Simple App", columns=6)

div = html.Div()
button = html.Button(children="Click Me")


@app.callback(dx.Output(div, "children"), dx.Input(button, "n_clicks"))
def callback(n_clicks):
   return "Clicked {} times".format(n_clicks)


tpl.add_component(button, label="Button to click", role="input")
tpl.add_component(div, role="output")

app.layout = tpl.layout(app)

if __name__ == "__main__":
   app.run_server()
```

![](https://i.imgur.com/sZ5HUrO.gif)

Templates provide a `.layout(app)` method that will construct a container of components that can be assigned to `app.layout`, or combined with other components to build `app.layout`.  

## template and app.callback integration
For convenience, `@app.callback` accepts an optional `template` argument. When provided, `@app.callback` will automatically add the provided input and output components to the template. Because of the information that `@app.callback` already has access to, it can choose reasonable defaults for the component's role and label.  Because the components will be added to the template, it becomes possible to construct the component inline in the `@app.callback` definition (rather than constructing them above and assigning them to local variables).  With these conveniences, the example above becomes:

[demos/template_system2.py](demos/template_system2.py)

```python
import dash_labs as dx
import dash_html_components as html
import dash

app = dash.Dash(__name__, plugins=[dx.Plugin()])
tpl = dx.templates.DbcCard(title="Simple App", columns=6)


@app.callback(
   dx.Output(html.Div(), "children"),
   dx.Input(html.Button(children="Click Me"), "n_clicks", label="Button to click"),
   template=tpl
)
def callback(n_clicks):
   return "Clicked {} times".format(n_clicks)


app.layout = tpl.layout(app)

if __name__ == "__main__":
   app.run_server()
```

## Component labels
When a template is populated using `@app.callback`, the label string for a component can be overridden using the `label` keyword argument to `dx.Input`/`dx.State`/`dx.Output`.  See the "Button to click" label added above. 

## Default output
When a template is provided, and no output is provided, the template will provide a default output container for the result of the function (usually an `html.Div` component).

[demos/template_system3.py](demos/template_system3.py)

```python
import dash_labs as dx
import dash_html_components as html
import dash

app = dash.Dash(__name__, plugins=[dx.Plugin()])
tpl = dx.templates.DbcCard(title="Simple App", columns=6)


@app.callback(
   dx.Input(html.Button(children="Click Me"), "n_clicks", label="Button to click"),
   template=tpl
)
def callback(n_clicks):
   return "Clicked {} times".format(n_clicks)


app.layout = tpl.layout(app)

if __name__ == "__main__":
   app.run_server()
```

## Accessing individual components to build custom layouts

### `CallbackWrapper`
The components added to a template are stored in the `.roles` property.  

This is a dictionary from template "roles" to `OrderedDict`s of `ArgumentComponents` (described below). All templates define at least two roles: `"input"` and `"output"`. By default, all components corresponding to the `@app.callback` `inputs` and `state` arguments are assigned the `"input"` role and therefore are included in the `.roles["input"]` `OrderedDict`. Similarly, all components corresponding to the `@app.callback` `output` argument are assigned the "output" role and therefore are included in the `.roles["output"]` `OrderedDict`.  Templates may define additional roles, and dependency values can be assigned to these roles using the `role` argument (e.g. `dx.Input(..., role="footer")`).

### ArgumentComponents
You might think that the values of the `.roles["inputs"]` and `.roles["output"]` dictionaries described above would simply be the components added to the template.  The reason it's not quite that simple is that for a single component added to a template, the template may create multiple components: There is the original input component, one for the label, and both of these may be wrapped in a container component.  Because the caller may want access to any, or all, of these components individually, references to all of these components, and their associated props, are stored in a `ArgumentComponents` instance.  Here are the attributes of `ArgumentComponents`, and an example of why a caller may want to access them.

 - `.arg_component`: This a reference to the innermost component that actually provides the callback function with an input value, which corresponds to the properties stored in `.arg_property` attribute. A caller would want to access this component in order to register additional callback functions to execute when the callback function is updated.
 - `.label_component`: This is the component that displays the label string for the component, where the label text is stored in the `.label_property` property of the component. A caller may want to access this component to customize the label styling, or access the current value of the label string.
 - `.container_component`: This is the outer-most component that contains all the other components described above, where the contained components are stored in the `.container_property` property of the container. This is generally the component that a caller should incorporate when building a custom layout.

This example uses `@app.callback` to add components to a template, constructs a fully custom layout, and defines custom callbacks on the components returned by `@app.callback`. This is loosely based on the Dash Bootstrap Components example at https://dash-bootstrap-components.opensource.faculty.ai/examples/iris/. 

Notice how custom callbacks are applied to the dropdowns returned by `@app.callback` to prevent specifying the same feature as both `x` and `y` values.

[demos/custom_layout_and_callback_integration.py](./demos/custom_layout_and_callback_integration.py)

```python
import dash_labs as dx
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
tpl = dx.templates.DbcSidebar(title="Iris Dataset")


# Use parameterize to create components
@app.callback(
   args=dict(
      x=dx.Input(dcc.Dropdown(options=feature_options, value="sepal_length")),
      y=dx.Input(dcc.Dropdown(options=feature_options, value="sepal_width")),
   ),
   template=tp
)
def iris(x, y):
   return dcc.Graph(
      figure=px.scatter(df, x=x, y=y, color="species"),
   )


# Get references to the dropdowns and register a custom callback to prevent the user
# from setting x and y to the same variable

# Get the dropdown components that were created by parameterize
x_component = tp.roles["input"]["x"].arg_component
y_component = tp.roles["input"]["y"].arg_component


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

x_container = tp.roles["input"]["x"].container_component
y_container = tp.roles["input"]["y"].container_component
output_component = tp.roles["output"][0].container_component

app.layout = html.Div([
   html.H1("Iris Feature Explorer"),
   html.H2("Select Features"),
   x_container,
   y_container,
   html.Hr(),
   html.H2("Feature Scatter Plot"),
   output_component
])

if __name__ == "__main__":
   app.run_server(debug=True)
```

![](https://i.imgur.com/MX4WaGS.gif)

## Adding additional components to a template

Additional components can be added to a template after the initial components are added by `@app.callback`.

Note how the `add_component` method supports `before` and `after` keyword arguments that can be used to insert new components at specific locations between components added by `app.callback`.

[demos/template_with_custom_additions.py](demos/template_with_custom_additions.py)

```python
import dash
import dash_labs as dx
import numpy as np
import dash_core_components as dcc
import plotly.express as px

app = dash.Dash(__name__, plugins=[dx.Plugin()])
template = dx.templates.DbcSidebar(title="Dash Labs App")


# import dash_core_components as dcc
@app.callback(
   inputs=dict(
      fun=dx.Input(dcc.Dropdown(
         options=[{"value": v, "label": v} for v in ["sin", "cos", "exp"]],
         value="sin",
      ), label="Function"),
      figure_title=dx.Input(dcc.Input(value="Initial Title"), label="Figure Title"),
      phase=dx.Input(dcc.Slider(min=1, max=10, value=3), label="Phase"),
      amplitude=dx.Input(dcc.Slider(min=1, max=10, value=4), label="Amplitude")
   ),
   template=template,
)
def function_browser(fun, figure_title, phase, amplitude):
   xs = np.linspace(-10, 10, 100)
   return dcc.Graph(figure=px.line(
      x=xs, y=getattr(np, fun)(xs + phase) * amplitude
   ).update_layout(title_text=figure_title))


# Add extra component to template
template.add_component(
   dcc.Markdown(children="# First Group"), role="input", before="fun"
)

template.add_component(dcc.Markdown(children=[
   "# Second Group\n"
   "Specify the Phase and Amplitudue for the chosen function"
]), role="input", before="phase")

template.add_component(dcc.Markdown(children=[
   "# H2 Title\n",
   "Here is the *main* plot"
]), role="output", before=0)

template.add_component(
   dcc.Link("Made with Dash", href="https://dash.plotly.com/"),
   component_property="children", role="output"
)

app.layout = tp.layout(app)

if __name__ == "__main__":
   app.run_server(debug=True)
```

![](https://i.imgur.com/VX6E6kD.png)

# Chapter 3: Template component constructors
To reduce the amount of boilerplate required to construct the dependency components to pass to `@app.callback`, template classes provide a variety of helper functions. A few examples are `tp.div()`, `tp.button()`, `tp.dropdown()`, etc.  These are relatively simple functions that return a dependency object. For example:

```python
tp.dropdown(["A", "B", "C"], label="My Dropdown")
```

evaluates to... 

```python
dx.Input(
    dcc.Dropdown(
      id={'uid': 'd4713d60-c8a7-0639-eb11-67b367a9c378'},
      options=[{'value': 'A', 'label': 'A'}, {'value': 'B', 'label': 'B'}, {'value': 'C', 'label': 'C'}],
      value='A',
      clearable=False
   ),
   "value",
   label="My Dropdown"
)
```

All of these functions provide the following keyword arguments:

 - `label`: The label to display for the component 
 - `role`: The template role of the component (`"input"`, `"output"`, or custom role defined by the template). If not provided, `app.callback` will assign components wrapped by `Input` or `State` dependencies as `"input"`, and those wrapped by `Output` as `"output"`
 - `component_property`: The property (or property grouping) considered to be the value of the component. This value is optional, and the template will provide a reasonable default for each component type (e.g. `n_clicks` for `dcc.Button`, `value` for `dcc.Dropdown`, `figure` for `dcc.Graph`).
 - `kind`: The dependency class to return. One of `dx.Input`, `dx.State`, or `dx.Output`. This value is optional and templates will provide a reasonable defaults (e.g. `dx.Input` for `dcc.Button` and `dcc.Dropdown`, `dx.Output` for `dcc.Graph`, etc.)
 - `id`: Optional argument to override the generated component id 
 - `opts`: Dictionary of keyword arguments to pass to the constructor of the component that is created.

In addition to these standard keyword arguments, conponent dependency builders also provide args to make the configuration of the components as concise as possible. e.g. `dx.dropdown(["A", "B", "C])`, `dx.slider(0, 10)`. 

These component dependency builders can significantly shorten many `@app.callback` specifications.

[demos/basic_decorator.py](./demos/basic_decorator.py)

```python
import dash
import dash_labs as dx
import numpy as np
import plotly.express as px

app = dash.Dash(__name__, plugins=[dx.Plugin()])
tp = dx.templates.dbc.DbcSidebar(title="Sample App")


@app.callback(
   args=dict(
      fun=tp.dropdown(["sin", "cos", "exp"], label="Function"),
      figure_title=tp.input("Initial Title", label="Figure Title"),
      phase=tp.slider(1, 10, label="Phase"),
      amplitude=tp.slider(1, 10, value=3, label="Amplitude"),
   ),
   template=tp
)
def greet(fun, figure_title, phase, amplitude):
   print(fun, figure_title, phase, amplitude)
   xs = np.linspace(-10, 10, 100)
   return tp.graph(figure=px.line(
      x=xs, y=getattr(np, fun)(xs + phase) * amplitude
   ).update_layout(title_text=figure_title))


app.layout = tp.layout(app)

if __name__ == "__main__":
   app.run_server(debug=True)
```
 
![](https://i.imgur.com/wqeZY0B.png)

## Component constructor specialization
Another advantage to the component constructor paradigm is that templates can specialize the representation of the different components. For example, Dash Bootstrap templates can use `dbc.Select` in place of `dcc.Dropdown` for `tp.dropdown()`. And DDK templates can use `ddk.Graph` in place of `dcc.Graph` for `tp.graph()`.

## Predefined templates

Here is a full example, specifying the `FlatDiv` template.  The following examples will only contain code for the template declaration line.

[demos/all_templates.py](./demos/all_templates.py)

```python
import dash
import dash_labs as dx
import numpy as np
import plotly.express as px

app = dash.Dash(__name__, plugins=[dx.Plugin()])
tp = dx.templates.FlatDiv()


@app.callback(
   args=dict(
      fun=tp.dropdown(["sin", "cos", "exp"], label="Function"),
      figure_title=tp.input("Initial Title", label="Figure Title"),
      phase=tp.slider(1, 10, label="Phase"),
      amplitude=tp.slider(1, 10, value=3, label="Amplitude"),
   ),
   output=tp.graph(),
   template=tp
)
def callback(fun, figure_title, phase, amplitude):
   xs = np.linspace(-10, 10, 100)
   np_fn = getattr(np, fun)

   # Let parameterize infer output component
   x = xs
   y = np_fn(xs + phase) * amplitude
   return px.line(x=x, y=y).update_layout(title_text=figure_title)


app.layout = tp.layout(app)

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
template = dx.templates.DccCard(title="Dash Labs App", width="500px")
```

![](https://i.imgur.com/387ygkJ.png)

### DbcCard

The `DbcCard` template introduces a dependency on the open source Dash Bootstrap Components library (https://dash-bootstrap-components.opensource.faculty.ai/).  It places all contents in a single bootstrap card, with a card title.

```python=
template = dx.templates.DbcCard(title="Dash Labs App", columns=6)
```

![](https://i.imgur.com/q6k008w.png)

### DbcRow

The `DbcRow` template places the inputs and outputs in separate cards and then arranges them in a Bootstrap row. This template is a great choice when integrating the components generated by `@app.callback` into a larger app made with Dash Bootstrap Components.

```python=
template = dx.templates.DbcRow(title="Dash Labs App")
```

![](https://i.imgur.com/sLaDDdS.png)

### DbcSidebar

The `DbcSidebar` template creates an app title bar and then includes the inputs in a sidebar on the left of the app, and the outputs in a card in the main app area.  This template is a great choice when using `@app.callback` to build an entire app.

```python=
template = dx.templates.DbcSidebar(title="Dash Labs App")
```

![](https://i.imgur.com/wqeZY0B.png)

### DdkCard

The `DdkCard` template introduces a dependency on the proprietary Dash Design Kit library that is included with Dash Enterprise.  Like `DbcCard`, in places all the outputs and inputs in a single card, along with a card title.

```python=
template = dx.templates.DdkCard(title="Dash Labs App", width=50)
```

![](https://i.imgur.com/kmX6fuP.png)

### DdkRow

Like the `DbcRow` template, `DdkRow` places the input and output components in separate cards, and then places those cards in a ddk row container.


```python=
template = dx.templates.DdkRow(title="Dash Labs App")
```

![](https://i.imgur.com/s29txGA.png)

### DdkSidebar

The `DdkSidebar` template creates a full app experience with an app header, a sidebar for the input controls, and a large main area for the output components.

```python=
template = dx.templates.DdkSidebar(title="Dash Labs App")
```

![](https://i.imgur.com/db8a8eo.png)

### Themed DbcSidebar

All of the `Dbc*` components can be themed using the Bootstrap themeing system. Simply pass the URL of a bootstrap theme css file as the `theme` argument of the template. Check out https://www.bootstrapcdn.com/bootswatch/ to browse available templates.

```python=
template = dx.templates.DbcSidebar(
    title="Dash Labs App", 
    theme="https://stackpath.bootstrapcdn.com/bootswatch/4.5.2/cyborg/bootstrap.min.css"
)
```

![](https://i.imgur.com/aKy415h.png)

### Themed DdkSidebar

Custom DDK themes created by hand, or using the DDK editor can be passed as the `theme` argument to any of the `Ddk*` templates.

Theme in [demos/ddk_theme.py](./demos/ddk_theme.py)

```python=
from my_theme import theme
template = dx.templates.DdkSidebar(title="Dash Labs App", theme=theme)
```

![](https://i.imgur.com/pcmRf1k.png)

## Creating custom templates
Custom templates can be created by subclassing the `dx.template.base.BaseTemplate` class. Or, for a custom Bootstrap Components template, subclass `dash.teamplates.dbc.BaseDbcTemplate`. Similarly, to create a custom DDK template, subclass `dx.templates.ddk.BaseDdkTemplate`.

Overriding a template may involve:
 1. Customizing the components that are constructed by "tp.dropdown", "tp.graph", etc.
 2. Specifying the representation of component labels.
 3. How component and label are group together into a container.
 4. How the input and output containers created in (3) are combined into a single layout container
 5. Providing custom inline CSS which gets inserted into `index.html`.
 6. Providing custom roles (in addition to "input" and "output").

# Chapter 4: More examples
Here are a few more examples of apps that make use of the templates and component dependency builders.

## Input components with multiple valuesk
Some components have multiple properties that could be considered the "value" of the component for the purpose of decorated  callback function. One common example is the `DatePickerRange` component.  For this component, the start date is stored in the `start_date` prop and the end date in the `end_date` prop.  To make it possible to pass both of these values to the function, the `component_properties` argument to `dx.Input` may be a tuple (or dict) of multiple properties.

In this example, the default value of the `component_properties` argument to `tp.date_picker_range` is the tuple `("start_date", "end_date")`, which results in a tuple of the corresponding component property values being passed to the decorated callback function.

Note: The explicit declarations of the two input arguments (without component dependency builders) are included in comments. 

[demos/multiple_component_props.py](./demos/multiple_component_props.py)

```python
import dash
import dash_labs as dx
import plotly.graph_objects as go
import dash_core_components as dcc

app = dash.Dash(__name__, plugins=[dx.Plugin()])
tp = dx.templates.FlatDiv()


@app.callback(
   args=dict(
      figure_title=tp.input("Figure Title", label="Graph Title"),
      # figure_title=dx.Input(dcc.Input(value="Figure Title"), label="Graph Title"),
      date_range=tp.date_picker_range(label="Date"),
      # date_range=dx.Input(dcc.DatePickerRange(), ("start_date", "end_date"), label="Date")
   ),
   template=tp
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


app.layout = tp.layout(app)

if __name__ == "__main__":
   app.run_server(debug=True)

```

![](https://i.imgur.com/shCO5Pz.gif)

## Manually executed function using state

The ipywidgets `@interact` decorator supports a `manual` argument. When `True`, an update button is automatically added and changes to the other widgets are not applied until the update button is clicked.  This workflow can be replicated with `@app.callback` by adding an `html.Button` component and specifying that all inputs other than the button should be classified as `State` (rather than the default of `Input`).  

Here is a full example of specifying all the components except the button as `kind=dx.State` to `@app.callback`.

[demos/basic_decorator_labels_state.py](./demos/basic_decorator_labels_state.py)

```python
import dash
import dash_labs as dx
import numpy as np
import dash_core_components as dcc
import plotly.express as px

app = dash.Dash(__name__, plugins=[dx.Plugin()])
tp = dx.templates.FlatDiv()


@app.callback(
   args=dict(
      fun=tp.dropdown(["sin", "cos", "exp"], label="Function", kind=dx.State),
      figure_title=tp.input("Initial Title", label="Figure Title", kind=dx.State),
      phase=tp.slider(1, 10, label="Phase", kind=dx.State),
      amplitude=tp.slider(1, 10, value=3, label="Amplitude", kind=dx.State),
      n_clicks=tp.button("Update", label=None)
   ),
   template=tp
)
def greet(fun, figure_title, phase, amplitude, n_clicks):
   print(fun, figure_title, phase, amplitude)
   xs = np.linspace(-10, 10, 100)
   return dcc.Graph(figure=px.line(
      x=xs, y=getattr(np, fun)(xs + phase) * amplitude
   ).update_layout(title_text=figure_title))


app.layout = tp.layout(app)

if __name__ == "__main__":
   app.run_server(debug=True)
```

![](https://i.imgur.com/8cd9KvF.gif)


## Custom output components
When a template is provided, the new `@app.callback` decorator no longer requires a caller to explicitly provide the output component that the callback function result will be stored in. The default behavior is to create an output `html.Div` component, and to store all the function results as the `children` property of this `Div`.  However, explicit output components and output properties can also be configured.

Here is an example that outputs a string to the `children` property of a `dcc.Markdown` component.

Note that the default value of `kind` for `tp.markdown` is `dx.Output`, which is why it's not necessary to override the `kind` argument. 

[demos/output_markdown.py](./demos/output_markdown.py)

```python
import dash
import dash_labs as dx

app = dash.Dash(__name__, plugins=[dx.Plugin()])
tp = dx.templates.DbcSidebar("App Title", sidebar_columns=6)


@app.callback(
   output=tp.markdown(),
   inputs=tp.textarea(
      "## Heading\n",
      opts=dict(style={"width": "100%", "height": 400})
   ),
   template=tp
)
def markdown_preview(input_text):
   return input_text


app.layout = tp.layout(app)

if __name__ == "__main__":
   app.run_server(debug=True)

```

![](https://i.imgur.com/vLbBF2R.gif)

# Chapter 5: The Component Plugin design pattern
Here is a proposed architecture that can be used to extract component creation and behavior into a separate class.  The `ComponentPlugin` class encapsulates the creation of inputs, output, and building (output value creation) functionality.

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
    def build(self, inputs_value):
        raise NotImplementedError
```

To make use of a `ComponentPlugin` subclass as a part of a callback, users would need to be trained to use the following pattern:

```python
...

plugin = FancyPlugin(**plugin_config)

@app.callback(
    inputs={
        input1=...,
        input2=...,
        plugin_values=plugin.inputs
    },
    outputs=[output1, plugin.output],
    template=tp,
)
def hello_plugin(input1, input2, plugin_values):
    # Do stuff with input1 and inputs2 to build result1 and, optionally,
    # build_config
    return result, plugin.build(plugin_values, **build_config)
    
...
```

The ability to pass components to `@app.callback` allows plugins to define their own input and output components, as well as define dependencies to make it possible to both input and output properties of the same component.  Following this pattern, the plugins do not need to define their own callbacks, making it much easier to compose plugins and connect them with custom functionality.

The tuple/dict grouping feature of `@app.callback` allow plugins to store any number of input and output components and make them look like a single value to the user. e.g. `plugin.inputs` and `plugin_values` above can be dictionaries with any number of keys, but the user can treat them as a single scalar value, so that they can always follow the same usage pattern.

## Component plugin example: DataTablePlugin
Here is an example of a fairly sophisticated plugin for displaying a `DataTable`. This plugin supports table paging, sorting, and filtering, and can be configured to operate in either clientside or serverside configurations.  While the clientside and serverside configuration logic is very different, involving the different callback properties, the user can switch between these modes using a single constructor argument.  

The clientside functionality is taken from https://dash.plotly.com/datatable/interactivity, and the serverside functionality is taken from https://dash.plotly.com/datatable/callbacks. 

Here is the full plugin definition (this is what would be defined in a reusable library)

```python
import math

from dash_labs.dependency import Output, Input
from dash_labs.util import build_id, filter_kwargs
from dash_labs.component_plugins.base import ComponentPlugin
from dash_labs.templates import FlatDiv
import pandas as pd
from dash_table import DataTable


class DataTablePlugin(ComponentPlugin):
   def __init__(
           self, df, columns=None, page_size=5, sort_mode=None, filterable=False,
           serverside=False, template=None
   ):
      if template is None:
         template = FlatDiv()

      if columns is None:
         columns = list(df.columns)

      self.page_size = page_size
      self.sort_mode = sort_mode
      self.filterable = filterable

      self.serverside = serverside
      self.page_count = self._compute_page_count(df)

      if self.serverside:
         self.full_df = df
         self.df = self._compute_serverside_dataframe_slice(df)
      else:
         self.full_df = df
         self.df = df

      self.data, self.columns = self.convert_data_columns(self.df, columns)

      self.template = template
      self.datatable_id = build_id()

      self._output = template._datatable_class()(
         id=self.datatable_id,
      )

   def _compute_serverside_dataframe_slice(self, full_df, page_current=None):
      if page_current is None:
         page_current = 0

      start_ind = page_current * self.page_size
      end_ind = start_ind + self.page_size
      return full_df.iloc[start_ind:end_ind]

   def _compute_page_count(self, full_df):
      return math.ceil(len(full_df) / self.page_size)

   def convert_data_columns(self, df, columns=None):
      # Handle DataFrame input
      if isinstance(df, pd.DataFrame):
         if columns is None:
            columns = df.columns.tolist()
         df = df.to_dict("records")

      # Handle columns as list
      if isinstance(columns, list) and columns and not isinstance(columns[0], dict):
         columns = [{"name": col, "id": col} for col in columns]

      return df, columns

   # Serverside helpers
   def _build_serverside_input(self):
      return {
         "page_current": Input(self.datatable_id, "page_current"),
         "sort_by": Input(self.datatable_id, "sort_by"),
         "filter_query": Input(self.datatable_id, "filter_query"),
      }

   def _build_serverside_output(self):
      data, columns = self.convert_data_columns(self.df, self.columns)
      result = Output(DataTable(
         data=data, columns=columns, id=self.datatable_id,
         page_current=0,
         page_size=self.page_size,
         page_action="custom",
         page_count=self._compute_page_count(self.full_df),
         **filter_kwargs(
            sort_action=None if self.sort_mode is None else "custom",
            sort_mode=self.sort_mode,
            filter_action="custom" if self.filterable else None,
            filter_query="" if self.filterable else None,
         )
      ), component_property=dict(
         data="data", columns="columns", page_count="page_count",
      ))
      return result

   def _build_serverside_result(self, inputs_value, df, preprocessed=False):
      page_current = inputs_value["page_current"]

      if not preprocessed:
         df = self.get_processed_dataframe(inputs_value, df)

      df_slice = self._compute_serverside_dataframe_slice(
         df, page_current=page_current
      )

      data, columns = self.convert_data_columns(df_slice)
      page_count = self._compute_page_count(df)
      return dict(data=data, columns=columns, page_count=page_count)

   # Clientside helpers
   def _build_clientside_input(self):
      return ()

   def _build_clientside_output(self):
      data, columns = self.convert_data_columns(self.df, self.columns)
      return Output(DataTable(
         data=data, columns=columns, id=self.datatable_id,
         page_size=self.page_size,
         **filter_kwargs(
            sort_action=None if self.sort_mode is None else "native",
            sort_mode=self.sort_mode,
            filter_action="native" if self.filterable else None
         )
      ), component_property=dict(
         data="data", columns="columns"
      ))

   def _build_clientside_result(self, df):
      if df is not None:
         data, columns = self.convert_data_columns(df)
      else:
         data, columns = self.data, self.columns

      return dict(data=data, columns=columns)

   @property
   def args(self):
      if self.serverside:
         return self._build_serverside_input()
      else:
         return self._build_clientside_input()

   @property
   def output(self):
      if self.serverside:
         return self._build_serverside_output()
      else:
         return self._build_clientside_output()

   def build(self, inputs_value, df=None, preprocessed=False):
      """

      :param inputs_value:
      :param df:
      :param preprocessed: Set to true if df was produced by get_processed_dataframe
      :return:
      """
      if self.serverside:
         return self._build_serverside_result(
            inputs_value, df, preprocessed=preprocessed
         )
      else:
         return self._build_clientside_result(df)

   def get_processed_dataframe(self, inputs_value, df):
      sort_by = inputs_value["sort_by"]
      # Get active dataframe
      if df is None:
         df = self.df
      # Perform filtering
      print("update serverside")
      if self.filterable and "filter_query" in inputs_value:
         filter_query = inputs_value["filter_query"]
         print(filter_query)
         df = _filter_serverside(df, filter_query)
      # Perform sorting
      if sort_by and len(sort_by):
         df = df.sort_values(
            [col['column_id'] for col in sort_by],
            ascending=[
               col['direction'] == 'asc'
               for col in sort_by
            ],
         )
      return df


operators = [['ge ', '>='],
             ['le ', '<='],
             ['lt ', '<'],
             ['gt ', '>'],
             ['ne ', '!='],
             ['eq ', '='],
             ['contains '],
             ['datestartswith ']]


def _split_filter_part(filter_part):
   for operator_type in operators:
      for operator in operator_type:
         if operator in filter_part:
            name_part, value_part = filter_part.split(operator, 1)
            name = name_part[name_part.find('{') + 1: name_part.rfind('}')]

            value_part = value_part.strip()
            v0 = value_part[0]
            if (v0 == value_part[-1] and v0 in ("'", '"', '`')):
               value = value_part[1: -1].replace('\\' + v0, v0)
            else:
               try:
                  value = float(value_part)
               except ValueError:
                  value = value_part

            # word operators need spaces after them in the filter string,
            # but we don't want these later
            return name, operator_type[0].strip(), value

   return [None] * 3


def _filter_serverside(df, filter_query):
   filtering_expressions = filter_query.split(' && ')
   dff = df

   for filter_part in filtering_expressions:
      col_name, operator, filter_value = _split_filter_part(filter_part)

      if operator in ('eq', 'ne', 'lt', 'le', 'gt', 'ge'):
         # these operators match pandas series operator method names
         dff = dff.loc[getattr(dff[col_name], operator)(filter_value)]
      elif operator == 'contains':
         dff = dff.loc[dff[col_name].str.contains(filter_value)]
      elif operator == 'datestartswith':
         # this is a simplification of the front-end filtering logic,
         # only works with complete fields in standard format
         dff = dff.loc[dff[col_name].str.startswith(filter_value)]

   return dff
```

Here is an example of an app that uses this plugin to create a `DataTable` that supports serverside paging, sorting, and filtering.

Note that the DataFrame that is input to the DataTable is first filtered using a Dropdown on the `sex` column of the dataset. This is an example of how plugins can support integration with the external logic of a callback. 

[demos/datatable_component_plugin.py](./demos/datatable_component_plugin.py)

```python
import plotly.express as px
import dash_labs as dx
import dash

df = px.data.tips()

app = dash.Dash(__name__, plugins=[dx.Plugin()])
tp = dx.templates.DbcCard(title="Table Component Plugin")

# serverside = False
serverside = True
table_plugin = dx.component_plugins.DataTablePlugin(
   df=df, page_size=10, sort_mode="single", filterable=True,
   serverside=serverside, template=tp
)


@app.callback(
   args=[
      tp.dropdown(["Male", "Female"], label="Patron Gender", clearable=True),
      table_plugin.args
   ],
   output=table_plugin.output,
   template=tp,
)
def callback(gender, plugin_input):
   if gender:
      filtered_df = df.query(f"sex == {repr(gender)}")
   else:
      filtered_df = df
   return table_plugin.build(plugin_input, filtered_df)


app.layout = tp.layout(app)

if __name__ == "__main__":
   app.run_server(debug=True)
```
![](https://i.imgur.com/2gsF4rC.gif)

And here is an example of using the same plugin to display the contents of the table (post filtering) in a plotly express figure:

[demos/datatable_component_plugin_and_graph.py](./demos/datatable_component_plugin_and_graph.py)

```python
import plotly.express as px
import dash_labs as dx
import dash

df = px.data.tips()

app = dash.Dash(__name__, plugins=[dx.Plugin()])
tp = dx.templates.DbcCard(title="Clientside Table Component Plugin")

# serverside = False
serverside = True
table_plugin = dx.component_plugins.DataTablePlugin(
   df=df, page_size=10, template=tp, sort_mode="single", filterable=True,
   serverside=serverside
)


@app.callback(
   args=[
      tp.dropdown(["Male", "Female"], label="Patron Gender", clearable=True),
      table_plugin.args
   ],
   output=[table_plugin.output, tp.graph()],
   template=tp,
)
def callback(gender, table_input):
   if gender:
      filtered_df = df.query(f"sex == {repr(gender)}")
   else:
      filtered_df = df

   dff = table_plugin.get_processed_dataframe(table_input, filtered_df)

   fig = px.scatter(
      dff, x="total_bill", y="tip", color="sex",
      color_discrete_map={"Male": "green", "Female": "orange"},
   )

   return [table_plugin.build(table_input, dff, preprocessed=True), fig]


app.layout = tp.layout(app)

if __name__ == "__main__":
   app.run_server(debug=True)
```

![](https://i.imgur.com/12burki.gif)

## Component plugin example: Image shape drawing
Here is a ComponentPlugin implementation of a shape drawing app similar to that described in https://dash.plotly.com/annotations.  This plugin displays two graphs, a greyscale image and a histogram of pixel intensities. The image graph is configured to draw a shape on the canvas on drag. The drawing of a shape causes the histogram to be updated to include only the pixels within the shape's.

```python
from dash_labs import build_id
from dash_labs.dependency import Output, Input
from .base import ComponentPlugin
import plotly.express as px
import plotly.graph_objects as go
import dash


class GreyscaleImageHistogramROI(ComponentPlugin):
   """
   Support dynamic labels and checkbox to disable input component
   """

   def __init__(
           self, img, template, image_label=None, histogram_label=None, newshape=None
   ):
      self.img = img

      if newshape is None:
         newshape = dict(
            fillcolor="lightgray", opacity=0.2, line=dict(color="black", width=8)
         )

      self.newshape = newshape

      self.image_fig = px.imshow(
         img, binary_string=True
      ).update_layout(
         dragmode="drawrect",
         margin=dict(l=20, b=20, r=20, t=20),
         newshape=self.newshape
      )

      self.image_graph_id = build_id("image-graph")
      self.histogram_graph_id = build_id("histogram-graph")
      self.template = template
      self.image_label = image_label
      self.histogram_label = histogram_label

   def _make_histrogram(self, x0, y0, x1, y1):
      if not all((x0, y0, x1, y1)):
         return {}

      roi_image = self.img[int(y0):int(y1), int(x0):int(x1)]

      return px.histogram(
         roi_image.ravel()
      ).update_layout(
         title_text="Intensity", showlegend=False
      ).update_xaxes(range=[0, 255])

   def _make_rect(self, x0, y0, x1, y1):
      if all((x0, y0, x1, y1)):
         return [dict({
            "editable": True,
            "type": "rect",
            "x0": x0,
            "y0": y0,
            "x1": x1,
            "y1": y1
         }, **self.newshape)]
      else:
         return []

   def _extract_pixel_bounds_from_shape(self, relayout_data):
      x0, y0, x1, y1 = (None,) * 4
      if "shapes" in relayout_data:
         shape = relayout_data["shapes"][-1]
         x0, y0 = shape["x0"], shape["y0"]
         x1, y1 = shape["x1"], shape["y1"]
      elif any(["shapes" in key for key in relayout_data]):
         x0 = [relayout_data[key] for key in relayout_data if "x0" in key][0]
         x1 = [relayout_data[key] for key in relayout_data if "x1" in key][0]
         y0 = [relayout_data[key] for key in relayout_data if "y0" in key][0]
         y1 = [relayout_data[key] for key in relayout_data if "y1" in key][0]

      # normalize coordinates and clamp to valid image boundaries
      if x0 and x1:
         if x0 > x1:
            x0, x1 = x1, x0
         x0 = 0 if x0 < 0 else x0
         x1 = self.img.shape[1] if x1 > self.img.shape[1] else x1
      if y0 and y1:
         if y0 > y1:
            y0, y1 = y1, y0
         y0 = 0 if y0 < 0 else y0
         y1 = self.img.shape[0] if y1 > self.img.shape[0] else y1

      return x0, y0, x1, y1

   @property
   def args(self):
      return self.template.graph(
         self.image_fig, kind=Input, component_property="relayoutData",
         id=self.image_graph_id, label=self.image_label
      )

   @property
   def output(self):
      return {
         "histogram_figure":
            self.template.graph(
               id=self.histogram_graph_id, label=self.histogram_label
            ),
         "image_figure": Output(self.image_graph_id, "figure")
      }

   def build(self, inputs_value):
      relayout_data = inputs_value
      if relayout_data:
         # shape coordinates are floats, we need to convert to ints for slicing
         x0, y0, x1, y1 = self._extract_pixel_bounds_from_shape(relayout_data)
         shapes = self._make_rect(x0, y0, x1, y1)

         new_image_fig = go.Figure(
            self.image_fig
         )
         new_image_fig.update_layout(shapes=shapes)

         return {
            "histogram_figure": self._make_histrogram(x0, y0, x1, y1),
            "image_figure": new_image_fig,
         }
      else:
         return {
            "histogram_figure": dash.no_update,
            "image_figure": dash.no_update,
         }
```

Here is an example of using the plugin

[demos/image_roi_histogram.py](./demos/image_roi_histogram.py)

```python
import dash
import dash_labs as dx
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
```

![](https://i.imgur.com/sjNCesU.gif)

## Component Plugin Example: Dynamic Label
Here is a component plugin that can be used to display a dynamic label for a component based on its value

```python
from dash_labs import build_id
from dash_labs.dependency import Output, Input
from .base import ComponentPlugin


class DynamicInputPlugin(ComponentPlugin):
   """
   Support dynamic labels and checkbox to disable input component
   """

   def __init__(self, input_dependency, template):
      self.input_dependency = input_dependency
      self.label_string = self.input_dependency.label
      self.label_id = build_id("label")
      self.label_prop = template._label_value_prop

      self.input_dependency.label = self.label_string
      self.input_dependency.label_id = self.label_id

   @property
   def args(self):
      return self.input_dependency

   @property
   def output(self):
      return dict(
         label_value=Output(self.label_id, self.label_prop),
      )

   def build(self, inputs_value):
      return dict(label_value=self._format_label(inputs_value))

   def _format_label(self, value):
      return self.label_string.format(value)

   def get_value(self, inputs_value):
      return inputs_value["value"]
```

And usage

[demos/dynamic_input_plugin.py](./demos/dynamic_input_plugin.py)

```python
import dash
import dash_labs as dx
import numpy as np
import dash_core_components as dcc
import plotly.express as px

app = dash.Dash(__name__, plugins=[dx.Plugin()])

tp = dx.templates.DbcSidebar(title="Dynamic Label Plugin")

phase_plugin = dx.component_plugins.DynamicInputPlugin(
   tp.slider(1, 10, value=4, label="Phase: {}"), template=tp
)


@app.callback(
   args=dict(
      fun=dx.Input(dcc.Dropdown(
         options=[{"value": v, "label": v} for v in ["sin", "cos", "exp"]],
         value="sin"
      ), label="Function"),
      phase=phase_plugin.args,
   ),
   output=[tp.graph(), phase_plugin.output],
   template=tp,
)
def callback(fun, phase):
   xs = np.linspace(-10, 10, 100)
   fig = px.line(
      x=xs, y=getattr(np, fun)(xs + phase)
   ).update_layout()

   return [fig, phase_plugin.build(phase)]


app.layout = tp.layout(app)

if __name__ == "__main__":
   app.run_server(debug=True)

```

![](https://i.imgur.com/pbHCvtV.gif)
