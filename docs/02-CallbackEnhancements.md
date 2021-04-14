# `@app.callback` Enhancements
This section describes core enhancements to `@app.callback` that are provided by the Dash Labs `FlexibleCallbacks` plugin.

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

Here the order of the callback's function arguments doesn't matter, only the names.

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
Because it is never ambiguous, Dash Labs supports freely mixing `Input` and `State` dependencies objects. This means that `State` dependencies can be included in the `inputs` argument, and `Input` dependencies can be included in the `state` argument.  To simplify things going forward, a new `args` keyword argument has been added that may contain a mix of `Input` and `State` dependencies. The recommended style with Dash Labs is to put both `Input` and `State` dependencies in `args` rather than using both `inputs` and `state`.

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
The Dash Labs `@app.callback` makes it possible to combine multiple `Input`/`State` dependency values into a single function argument. As we'll see in Chapter 5, this opens up powerful component+behavior encapsulation workflows.

> In other contexts, unpacking grouped values like this is sometimes referred to as destructuring.

### Tuple grouping
Dependency values can be grouped in a tuple. Here the `ab` keyword function argument is a tuple consisting of the values of two `Input` dependency values.

```python
@app.callback(
    output=[Output(...), Output(...)],
    args=dict(
        ab=(Input(...), Input(...)),
        c=Input(...)
    )
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
Dash Labs makes it possible to include a component instance in place of a component id in the `Input`, `State`, and `Output` dependency objects.  This feature is currently provided by the special `dl.Input`, `dl.State`, `dl.Output` classes. Dash Labs apps should use these classes in place of the Dash 1 `dash.dependency.Input`, `State`, and `Output` classes.  

```python
import dash_labs as dl
...
div = html.Div()
button = html.Button(children="Click Me")

@app.callback(dl.Output(div, "children"), dl.Input(button, "n_clicks"))
def callback(n_clicks):
    return "Clicked {} times".format(n_clicks)

# Include div and button in app.layout below
...
```

The `component_property` specification in the dependency object can be a single property as a string (as in Dash 1), or it can be a tuple or dictionary grouping of multiple properties of the component.  Here is an example with the `DatePickerRange` component:

```python
div = html.Div()
date_picker_range = dcc.DatePickerRange()
@app.callback(Output(div, "children"), Input(date_picker_range, ("start_date", "end_date")))
def callback(date_range):
    start_date, end_date = date_range
    return "Start date: {}\n End date: {}".format(start_date, end_date)
```

## Component id's
If a component does not have an id when it is wrapped in a dependency, a unique id is created and assigned to the component automatically. These unique IDs are generated deterministically (not randomly) in order to be consistent across processes.
