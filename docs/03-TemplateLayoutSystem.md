# The template layout system
Dash Labs introduces a template system that makes it possible to quickly add components to a pre-defined template.  

## Manually add components to a template
As will be described below, the template system integrates with `@app.callback`, but templates can also be used independently of `@app.callback`.

Templates that are included with Dash Labs are located in the `dl.templates` package.  The convention is to assign a template instance to a variable named `tpl`. Components can then be added to the template with `tpl.add_component` 

Here is a simple example of manually adding components to a `DbcCard` template 

[demos/template_system1.py](demos/template_system1.py)

```python
import dash_labs as dl
import dash_html_components as html
import dash_bootstrap_components as dbc
import dash

app = dash.Dash(__name__, plugins=[dl.plugins.FlexibleCallbacks()])
tpl = dl.templates.DbcCard(app, title="Simple App", columns=4)

div = html.Div()
button = html.Button(children="Click Me")

@app.callback(dl.Output(div, "children"), dl.Input(button, "n_clicks"))
def callback(n_clicks):
    return "Clicked {} times".format(n_clicks)

tpl.add_component(button, label="Button to click", role="input")
tpl.add_component(div, role="output")

app.layout = dbc.Container(fluid=True, children=tpl.children)

if __name__ == "__main__":
    app.run_server(debug=True)
```

![](https://i.imgur.com/eSRujx6.gif)

### Component role
When a component is added to a template using `add_component`, it is associated with a template role using the `role` argument. Components that share the same role will be grouped together by the template in the component layout it produces. All templates support the `"input"` and `"output"` roles, and individual templates may provide support for additional roles.

### Component label
When a component is added to a template using `add_component`, it may optionally be associated with a label string using the `label` argument. When provided, the template will wrap the provided component with a label in the component layout it produces.

### Template `children`
Templates provide a `.children` property that returns a container that includes the components that were added to the template.  This container is a regular Dash component that can be assigned to `app.layout`, or combined with other components to build `app.layout`.

> Note: When using a template based on Dash Bootstrap Components, it's recommended to use `dbc.Container` as the top-level layout component, and to assign the template's children as the children of the `dbc.Container`. See https://dash-bootstrap-components.opensource.faculty.ai/docs/components/layout/ for more information.  Similarly, when using a template based on Dash Design Kit, it's recommended to use `ddk.App` as the top-level layout component, and to assign the template's children as the children of the `ddk.App`.  

## template and app.callback integration
For convenience, `@app.callback` accepts an optional `template` argument. When provided, `@app.callback` will automatically add the provided input and output components to the template. Because of the information that `@app.callback` already has access to, it can choose reasonable defaults for each component's `role` and `label`.  Because the components will be added to the template, it becomes possible to construct components inline in the `@app.callback` definition, rather than constructing them above and assigning them to local variables.  With these conveniences, the example above becomes:

[demos/template_system2.py](demos/template_system2.py)

```python
import dash_labs as dl
import dash_html_components as html
import dash_bootstrap_components as dbc
import dash

app = dash.Dash(__name__, plugins=[dl.plugins.FlexibleCallbacks()])
tpl = dl.templates.DbcCard(app, title="Simple App", columns=6)

@app.callback(
    dl.Output(html.Div(), "children"),
    dl.Input(html.Button(children="Click Me"), "n_clicks", label="Button to click"),
    template=tpl,
)
def callback(n_clicks):
    return "Clicked {} times".format(n_clicks)

app.layout = dbc.Container(fluid=True, children=tpl.children)

if __name__ == "__main__":
    app.run_server(debug=True)
```

![](https://i.imgur.com/eSRujx6.gif)

### Customize labels and roles
When a template is populated using `@app.callback`, the label string and role for a component can be overridden using the `label` and `role` keyword arguments to `dl.Input`/`dl.State`/`dl.Output`.  See the "Button to click" label added above. 

## Default output
When a template is provided, and no `Output` dependency is provided, the template will provide a default output container for the result of the function (typically an `html.Div` component).

[demos/template_system3.py](demos/template_system3.py)

```python
import dash_labs as dl
import dash_html_components as html
import dash_bootstrap_components as dbc
import dash

app = dash.Dash(__name__, plugins=[dl.plugins.FlexibleCallbacks()])
tpl = dl.templates.DbcCard(app, title="Simple App", columns=6)

@app.callback(
    dl.Input(html.Button(children="Click Me"), "n_clicks", label="Button to click"),
    template=tpl,
)
def callback(n_clicks):
    return "Clicked {} times".format(n_clicks)

app.layout = dbc.Container(fluid=True, children=tpl.children)

if __name__ == "__main__":
    app.run_server(debug=True)
```

![](https://i.imgur.com/eSRujx6.gif)

## Template component constructors
To reduce the amount of boilerplate required to construct the dependency components to pass to `@app.callback`, template classes provide a variety of helper functions. A few examples are `tpl.div_output()`, `tpl.button_input()`, `tpl.dropdown_input()`, etc.  These are relatively simple class methods that return a dependency object. For example:

```python
tpl.dropdown_input(["A", "B", "C"], label="My Dropdown")
```

evaluates to... 

```python
dl.Input(
    dcc.Dropdown(
      id={'uid': 'd4713d60-c8a7-0639-eb11-67b367a9c378'},
      options=[
        {'value': 'A', 'label': 'A'}, 
        {'value': 'B', 'label': 'B'},
        {'value': 'C', 'label': 'C'}
      ],
      value='A',
      clearable=False
   ),
   "value",
   label="My Dropdown"
)
```

All of these functions provide the following keyword arguments:

 - `label`: The label to display for the component 
 - `role`: The template role of the component (`"input"`, `"output"`, or custom role defined by the template). The `role` defaults to the method suffix (e.g. the role of `tpl.dropdown_input()` is `"input"`).
 - `component_property`: The property (or property grouping) considered to be the value of the component. This value is optional, and the template will provide a reasonable default for each component type (e.g. `n_clicks` for `dcc.Button`, `value` for `dcc.Dropdown`, `figure` for `dcc.Graph`).
 - `kind`: The dependency class to return. One of `dl.Input`, `dl.State`, or `dl.Output`. This value is optional and templates will provide a reasonable defaults (e.g. `dl.Input` for `dcc.Button` and `dcc.Dropdown`, `dl.Output` for `dcc.Graph`, etc.)
 - `id`: Optional argument to override the generated component id 
 - `opts`: Dictionary of keyword arguments to pass to the constructor of the component that is created.

In addition to these standard keyword arguments, component dependency builders also provide args to make the configuration of the components as concise as possible. e.g. `dl.dropdown_input(["A", "B", "C])`, `dl.slider_input(0, 10)`. 

These component dependency builders can significantly shorten many `@app.callback` specifications.

Here is an update to the previous example that uses the `tpl.button_input` component constructor instead of manually creating `dl.Input` and `html.Button` objects.

[demos/template_system4.py](demos/template_system4.py)

```python
import dash_bootstrap_components as dbc
import dash_labs as dl
import dash

app = dash.Dash(__name__, plugins=[dl.plugins.FlexibleCallbacks()])
tpl = dl.templates.DbcCard(app, title="Simple App", columns=6)

@app.callback(
    tpl.button_input("Click Me", label="Button to click"),
    template=tpl,
)
def callback(n_clicks):
    return "Clicked {} times".format(n_clicks)

app.layout = dbc.Container(fluid=True, children=tpl.children)

if __name__ == "__main__":
    app.run_server(debug=True)
```

![](https://i.imgur.com/53XDlQ1.gif)

## Component constructor specialization
Another advantage of the component constructor paradigm is that templates can specialize the representation of the different components. For example, Dash Bootstrap templates can use `dbc.Select` in place of `dcc.Dropdown` for `tpl.dropdown_input()`. And DDK templates can use `ddk.Graph` in place of `dcc.Graph` for `tpl.graph_output()`.

## Manually executed function using state

The ipywidgets `@interact` decorator supports a `manual` argument. When `True`, an update button is automatically added and changes to the other widgets are not applied until the update button is clicked.  This workflow can be replicated with `@app.callback` by adding a button component and specifying that all inputs other than the button should be classified as `State` (rather than the default of `Input`).  

Here is a full example of specifying all the components except the button as `kind=dl.State` to `@app.callback`.

[demos/basic_decorator_manual.py](./demos/basic_decorator_manual.py)

```python
import dash
import dash_labs as dl
import numpy as np
import dash_core_components as dcc
import plotly.express as px
import dash_bootstrap_components as dbc

app = dash.Dash(__name__, plugins=[dl.plugins.FlexibleCallbacks()])
tpl = dl.templates.DbcRow(app, title="Manual Update", theme=dbc.themes.SOLAR)

@app.callback(
    args=dict(
        fun=tpl.dropdown_input(["sin", "cos", "exp"], label="Function", kind=dl.State),
        figure_title=tpl.textbox_input(
            "Initial Title", label="Figure Title", kind=dl.State
        ),
        phase=tpl.slider_input(1, 10, label="Phase", kind=dl.State),
        amplitude=tpl.slider_input(1, 10, value=3, label="Amplitude", kind=dl.State),
        n_clicks=tpl.button_input("Update", label=None),
    ),
    template=tpl,
)
def greet(fun, figure_title, phase, amplitude, n_clicks):
    print(fun, figure_title, phase, amplitude)
    xs = np.linspace(-10, 10, 100)
    return dcc.Graph(
        figure=px.line(x=xs, y=getattr(np, fun)(xs + phase) * amplitude).update_layout(
            title_text=figure_title
        )
    )

app.layout = dbc.Container(fluid=True, children=tpl.children)

if __name__ == "__main__":
    app.run_server(debug=True)
```

![](https://i.imgur.com/U9iieJC.gif)


## Custom output components
When a template is provided, the new `@app.callback` decorator no longer requires a caller to explicitly provide the output component that the callback function result will be stored in. However, explicit output components and output properties can still be configured.

Here is an example that outputs a string to the `children` property of an `dcc.Markdown` component.

Note that the default value of `kind` for `tpl.markdown_output` is `dl.Output`, which is why it's not necessary to override the `kind` argument. 

[demos/output_markdown.py](./demos/output_markdown.py)

```python
import dash
import dash_labs as dl
import dash_bootstrap_components as dbc

app = dash.Dash(__name__, plugins=[dl.plugins.FlexibleCallbacks()])
tpl = dl.templates.DbcSidebar(app, "App Title", sidebar_columns=6)

@app.callback(
    output=tpl.markdown_output(),
    inputs=tpl.textarea_input(
        "## Heading\n", opts=dict(style={"width": "100%", "height": 400})
    ),
    template=tpl,
)
def markdown_preview(input_text):
    return input_text

app.layout = dbc.Container(fluid=True, children=tpl.children)

if __name__ == "__main__":
    app.run_server(debug=True)
```

![](https://i.imgur.com/qO1p7hK.gif)

## Adding additional components to a template

Additional components can be added to a template after the initial components are added by `@app.callback`.

Note how the `add_component` method supports `before` and `after` keyword arguments that can be used to insert new components at specific locations between components added by `app.callback`.

[demos/template_with_custom_additions.py](demos/template_with_custom_additions.py)

```python
import dash
import dash_labs as dl
import numpy as np
import dash_core_components as dcc
import dash_bootstrap_components as dbc
import plotly.express as px

app = dash.Dash(__name__, plugins=[dl.plugins.FlexibleCallbacks()])
tpl = dl.templates.DbcSidebar(app, title="Dash Labs App")

# import dash_core_components as dcc
@app.callback(
    inputs=dict(
        fun=tpl.dropdown_input(["sin", "cos", "exp"], label="Function"),
        figure_title=tpl.textbox_input("Initial Title", label="Figure Title"),
        phase=tpl.slider_input(1, 10, value=3, label="Phase"),
        amplitude=tpl.slider_input(1, 10, value=4, label="Amplitude"),
    ),
    output=tpl.graph_output(),
    template=tpl,
)
def function_browser(fun, figure_title, phase, amplitude):
    xs = np.linspace(-10, 10, 100)
    return px.line(x=xs, y=getattr(np, fun)(xs + phase) * amplitude).update_layout(
        title_text=figure_title
    )

# Add extra component to template
tpl.add_component(dcc.Markdown(children="# First Group"), role="input", before="fun")

tpl.add_component(
    dcc.Markdown(
        children=[
            "# Second Group\n"
            "Specify the Phase and Amplitudue for the chosen function"
        ]
    ),
    role="input",
    before="phase",
)

tpl.add_component(
    dcc.Markdown(children=["# H2 Title\n", "Here is the *main* plot"]),
    role="output",
    before=0,
)

tpl.add_component(
    dcc.Link("Made with Dash", href="https://dash.plotly.com/"),
    component_property="children",
    role="output",
)

app.layout = dbc.Container(fluid=True, children=tpl.children)

if __name__ == "__main__":
    app.run_server(debug=True)
```

![](https://i.imgur.com/AW53Sun.png)


## Accessing individual components to build custom layouts

### `CallbackWrapper`
The components added to a template are stored in the `.roles` property.  

This is a dictionary from template `roles` to `OrderedDict`s of `ArgumentComponents` (described below). All templates define at least two roles: `"input"` and `"output"`. By default, all components corresponding to the `@app.callback` `inputs` and `state` arguments are assigned the `"input"` role and therefore are included in the `.roles["input"]` `OrderedDict`. Similarly, all components corresponding to the `@app.callback` `output` argument are assigned the "output" role and therefore are included in the `.roles["output"]` `OrderedDict`.  Templates may optionally define additional roles, and dependency values can be assigned to these roles using the `role` argument (e.g. `dl.Input(..., role="footer")`).

### ArgumentComponents
You might think that the values of the `.roles["inputs"]` and `.roles["output"]` dictionaries described above would simply be the components added to the template.  The reason it's not quite that simple is that for a single component added to a template, the template may create multiple components: There is the original component, one for the label, and both of these may be wrapped in a container component.  Because the caller may want access to any, or all, of these components individually, references to all of these components, and their associated props, are stored in a `ArgumentComponents` instance.  Here are the attributes of `ArgumentComponents`, and an example of why a caller may want to access them.

 - `.arg_component`: This a reference to the innermost component that actually provides the callback function with an input value, which corresponds to the properties stored in `.arg_property` attribute. A caller would want to access this component in order to register additional callback functions to execute when the callback function is updated.
 - `.label_component`: This is the component that displays the label string for the component, where the label text is stored in the `.label_property` property of the component. A caller may want to access this component to customize the label styling, or access the current value of the label string.
 - `.container_component`: This is the outer-most component that contains all the other components described above, where the contained components are stored in the `.container_property` property of the container. This is generally the component that a caller should incorporate when building a custom layout.

This example uses `@app.callback` to add components to a template, constructs a fully custom layout, and defines custom callbacks on the components returned by `@app.callback`. This is loosely based on the Dash Bootstrap Components example at https://dash-bootstrap-components.opensource.faculty.ai/examples/iris/. 

Notice how custom callbacks are applied to the dropdowns returned by `@app.callback` to prevent specifying the same feature as both `x` and `y` values.

[demos/custom_layout_and_callback_integration.py](./demos/custom_layout_and_callback_integration.py)

```python
# Based on https://dash-bootstrap-components.opensource.faculty.ai/examples/iris/

import dash_labs as dl
import plotly.express as px
import dash_core_components as dcc
import dash_html_components as html
import dash_bootstrap_components as dbc
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
app = dash.Dash(__name__, plugins=[dl.plugins.FlexibleCallbacks()])
tpl = dl.templates.DbcSidebar(app, title="Iris Dataset")

# Use parameterize to create components
@app.callback(
    args=dict(
        x=dl.Input(dcc.Dropdown(options=feature_options, value="sepal_length")),
        y=dl.Input(dcc.Dropdown(options=feature_options, value="sepal_width")),
    ),
    template=tpl,
)
def iris(x, y):
    return dcc.Graph(
        figure=px.scatter(df, x=x, y=y, color="species"),
    )

# Get references to the dropdowns and register a custom callback to prevent the user
# from setting x and y to the same variable

# Get the dropdown components that were created by parameterize
x_component = tpl.roles["input"]["x"].arg_component
y_component = tpl.roles["input"]["y"].arg_component


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

x_container = tpl.roles["input"]["x"].container_component
y_container = tpl.roles["input"]["y"].container_component
output_component = tpl.roles["output"][0].container_component

app.layout = html.Div(
    [
        html.H1("Iris Feature Explorer"),
        html.H2("Select Features"),
        x_container,
        y_container,
        html.Hr(),
        html.H2("Feature Scatter Plot"),
        output_component,
    ]
)

if __name__ == "__main__":
    app.run_server(debug=True)
```

![](https://i.imgur.com/RfnVJ8a.gif)
