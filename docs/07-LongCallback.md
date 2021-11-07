
> ## Status: Long Callbacks
> #### The long callback handling was added to Dash 2.0 🎉
> #### See the [Long Callback section](https://dash.plotly.com/long-callbacks) in the Dash documentation 


```diff
- ----------------------------------------------------------------------------------
-  This documentation describes code in a previous version of dash-labs (v0.4.0) 
-  and is included here for legacy purposes only.
-
-  You can install v0.4.0 with:
-  pip install dash-labs==0.4.0
- ----------------------------------------------------------------------------------
```




# Overview
DashLabs introduces a new callback decorator called `@long_callback`. This decorator is designed to make it easier to create callback functions that take a long time to run, without locking up the Dash app or timing out.

`@long_callback` supports multiple backend executors.  Two backends are currently implemented:
 - A [diskcache](http://www.grantjenks.com/docs/diskcache/index.html) backend that runs callback logic in a separate process and stores the results to disk using the diskcache library. This is the easiest backend to use for local development.
 - A [Celery](https://docs.celeryproject.org/en/stable/getting-started/introduction.html) backend that runs callback logic in a celery worker and returns results to the Dash app through a Celery broker like RabbitMQ or Redis.

The `@long_callback` decorator supports the same arguments as the normal `@callback` decorator, but also includes support for 3 additional arguments that will be discussion below: `running`, `cancel`, and `progress`.

## Enabling long-callback support
In Dash Labs, the `@long_callback` decorator is enabled using the `LongCallback` plugin.  To support multiple backends, the `LongCallback` plugin is, itself, configured with either a `DiskcacheCachingCallbackManager` or `CeleryCallbackManager` object.  Furthermore, in addition to the `LongCallback` plugin, the `FlexibleCallback` and `HiddenComponents` plugins must be enabled as well.  Here is an example of configuring an app to enable the `@long_callback` decorator using the diskcache backend.

```python
import dash
import dash_labs as dl

## Diskcache
import diskcache
cache = diskcache.Cache("./cache")
long_callback_manager = dl.plugins.DiskcacheCachingCallbackManager(cache)

app = dash.Dash(__name__, plugins=[
    dl.plugins.FlexibleCallbacks(),
    dl.plugins.HiddenComponents(),
    dl.plugins.LongCallback(long_callback_manager)
])
```

This configuration requires the `diskcache` package which can be installed with:
```
$ pip install diskcache
```

Additionally, on Windows the `multiprocess` library is required as well.

```
$ pip install multiprocess
```

## Example 1: Simple background callback
Here is a simple example of using the `@long_callback` decorator to register a callback function that updates an `html.P` element with the number of times that a button has been clicked.  The callback uses `time.sleep` to simulate a long-running operation.  

```python
import time
import dash
import dash_html_components as html
import dash_labs as dl

## Diskcache
import diskcache
cache = diskcache.Cache("./cache")
long_callback_manager = dl.plugins.DiskcacheCachingCallbackManager(cache)

app = dash.Dash(__name__, plugins=[
    dl.plugins.FlexibleCallbacks(),
    dl.plugins.HiddenComponents(),
    dl.plugins.LongCallback(long_callback_manager)
])

app.layout = html.Div([
    html.Div([
        html.P(id="paragraph_id", children=["Button not clicked"])
    ]),
    html.Button(id='button_id', children="Run Job!"),
])


@app.long_callback(
    output=dl.Output("paragraph_id", "children"),
    args=dl.Input("button_id", "n_clicks"),
)
def callback(n_clicks):
    time.sleep(2.0)
    return [f"Clicked {n_clicks} times"]


if __name__ == "__main__":
    app.run_server(debug=True)
```

![](https://i.imgur.com/T7442iY.gif)

## Example 2: Disable button while callback is running
In the previous example, there is no visual indication that the long callback was running. It is also possible to click the "Run Job!" button multiple times before the original job has the chance to complete.  This example addresses these shortcomings by disabling the button while the callback is running, and re-enabling it when the callback completes.

This is accomplished using the `running` argument to `@long_callback`.  This argument accepts a list of 3-element tuples.  The first element of each tuple should be an `Output` dependency object referencing a property of a component in the app layout. The second elements is the values that the property should be set to while the callback is running, and the third element is the value the property should be set to when the callback completes.

This example uses `running` to set the `disabled` property of the button to `True` while the callback is running, and `False` when it completes.

```python
import time
import dash
import dash_html_components as html
import dash_labs as dl

## Diskcache
import diskcache
cache = diskcache.Cache("./cache")
long_callback_manager = dl.plugins.DiskcacheCachingCallbackManager(cache)

app = dash.Dash(__name__, plugins=[
    dl.plugins.FlexibleCallbacks(),
    dl.plugins.HiddenComponents(),
    dl.plugins.LongCallback(long_callback_manager)
])

app.layout = html.Div([
    html.Div([
        html.P(id="paragraph_id", children=["Button not clicked"])
    ]),
    html.Button(id='button_id', children="Run Job!"),
])

@app.long_callback(
    output=dl.Output("paragraph_id", "children"),
    args=dl.Input("button_id", "n_clicks"),
    running=[
        (dl.Output("button_id", "disabled"), True, False),
    ],
)
def callback(n_clicks):
    time.sleep(2.0)
    return [f"Clicked {n_clicks} times"]


if __name__ == "__main__":
    app.run_server(debug=True)
```

![](https://i.imgur.com/zjoq1I6.gif)

## Example 3: Cancelable callback
This example builds on the previous example, adding support for canceling a long-running callback using the `cancel` argument to the `@long_callback` decorator.  The `cancel` argument should be set to a list of `Input` dependency objects that reference a property of a component in the app's layout.  When the value of this property changes while a callback is running, the callback is canceled.  Note that the value of the property is not significant, any change in value will result in the cancellation of the running job (if any).

```python
import time
import dash
import dash_html_components as html
import dash_labs as dl

## Diskcache
import diskcache
cache = diskcache.Cache("./cache")
long_callback_manager = dl.plugins.DiskcacheCachingCallbackManager(cache)

app = dash.Dash(__name__, plugins=[
    dl.plugins.FlexibleCallbacks(),
    dl.plugins.HiddenComponents(),
    dl.plugins.LongCallback(long_callback_manager)
])

app.layout = html.Div([
    html.Div([
        html.P(id="paragraph_id", children=["Button not clicked"])
    ]),
    html.Button(id='button_id', children="Run Job!"),
    html.Button(id='cancel_button_id', children="Cancel Running Job!"),
])

@app.long_callback(
    output=dl.Output("paragraph_id", "children"),
    args=dl.Input("button_id", "n_clicks"),
    running=[
        (dl.Output("button_id", "disabled"), True, False),
        (dl.Output("cancel_button_id", "disabled"), False, True),
    ],
    cancel=[dl.Input("cancel_button_id", "n_clicks")],
)
def callback(n_clicks):
    time.sleep(2.0)
    return [f"Clicked {n_clicks} times"]


if __name__ == "__main__":
    app.run_server(debug=True)
```

![](https://i.imgur.com/EzzLimH.gif)

## Example 4: Progress bar
This example uses the `progress` argument to the `@long_callback` decorator to update a progress bar while the callback is running.  The `progress` argument should be set to an `Output` dependency grouping that references properties of components in the app's layout.

When a dependency grouping is assigned to the `progress` argument of `@long_callback`, the decorated function will be called with a new special argument as the first argument to the function.  This special argument, named `set_progress` in the example below, is a function handle that the decorated function should call in order to provide updates to the app on its current progress.  The `set_progress` function accepts a single argument, which correspond to the grouping of properties specified in the `Output` dependency grouping passed to the `progress` argument of `@long_callback`.

```python
import time
import dash
import dash_html_components as html
import dash_labs as dl

## Diskcache
import diskcache
cache = diskcache.Cache("./cache")
long_callback_manager = dl.plugins.DiskcacheCachingCallbackManager(cache)

app = dash.Dash(__name__, plugins=[
    dl.plugins.FlexibleCallbacks(),
    dl.plugins.HiddenComponents(),
    dl.plugins.LongCallback(long_callback_manager)
])

app.layout = html.Div([
    html.Div([
        html.P(id="paragraph_id", children=["Button not clicked"]),
        html.Progress(id="progress_bar"),
    ]),
    html.Button(id='button_id', children="Run Job!"),
    html.Button(id='cancel_button_id', children="Cancel Running Job!"),
])

@app.long_callback(
    output=dl.Output("paragraph_id", "children"),
    args=dl.Input("button_id", "n_clicks"),
    running=[
        (dl.Output("button_id", "disabled"), True, False),
        (dl.Output("cancel_button_id", "disabled"), False, True),
        (dl.Output("paragraph_id", "style"), {"visibility": "hidden"}, {"visibility": "visible"}),
        (dl.Output("progress_bar", "style"), {"visibility": "visible"}, {"visibility": "hidden"}),
    ],
    cancel=[dl.Input("cancel_button_id", "n_clicks")],
    progress=dl.Output("progress_bar", ("value", "max")),
)
def callback(set_progress, n_clicks):
    total = 10
    for i in range(total):
        time.sleep(0.5)
        set_progress((str(i + 1), str(total)))

    return [f"Clicked {n_clicks} times"]

if __name__ == "__main__":
    app.run_server(debug=True)
```

![](https://i.imgur.com/0tRGCH8.gif)

## Example 5: Progress bar chart graph
The `progress` argument to the `@long_callback` decorator can be used to update arbitrary component properties.  This example creates and updates a plotly bar graph to display the current calculation status.  This example also uses the `progress_default` argument to `long_callback` to specify a grouping of values that should be assigned to the components specified by the `progress` argument when the callback is not in progress. If `progress_default` is not provided, all the dependency properties specified in `progress` will be set to `None` when the callback is not running.  In this case, `progress_default` is set to a figure with a zero width bar. 

```python
import time
import dash
import dash_html_components as html
import dash_core_components as dcc
import dash_labs as dl
from dash_labs.plugins import DiskcacheCachingCallbackManager
import plotly.graph_objects as go

## Diskcache
import diskcache
cache = diskcache.Cache("./cache")
long_callback_manager = DiskcacheCachingCallbackManager(cache)

def make_progress_graph(progress, total):
    progress_graph = (
        go.Figure(data=[go.Bar(x=[progress])])
        .update_xaxes(range=[0, total])
        .update_yaxes(
            showticklabels=False,
        )
        .update_layout(height=100, margin=dict(t=20, b=40))
    )
    return progress_graph

app = dash.Dash(
    __name__,
    plugins=[
        dl.plugins.FlexibleCallbacks(),
        dl.plugins.HiddenComponents(),
        dl.plugins.LongCallback(long_callback_manager),
    ],
)

app.layout = html.Div(
    [
        html.Div(
            [
                html.P(id="paragraph_id", children=["Button not clicked"]),
                dcc.Graph(id="progress_bar_graph", figure=make_progress_graph(0, 10)),
            ]
        ),
        html.Button(id="button_id", children="Run Job!"),
        html.Button(id="cancel_button_id", children="Cancel Running Job!"),
    ]
)

@app.long_callback(
    output=dl.Output("paragraph_id", "children"),
    args=dl.Input("button_id", "n_clicks"),
    running=[
        (dl.Output("button_id", "disabled"), True, False),
        (dl.Output("cancel_button_id", "disabled"), False, True),
        (
            dl.Output("paragraph_id", "style"),
            {"visibility": "hidden"},
            {"visibility": "visible"},
        ),
        (
            dl.Output("progress_bar_graph", "style"),
            {"visibility": "visible"},
            {"visibility": "hidden"},
        ),
    ],
    cancel=[dl.Input("cancel_button_id", "n_clicks")],
    progress=dl.Output("progress_bar_graph", "figure"),
    progress_default=make_progress_graph(0, 10),
    interval=1000,
)
def callback(set_progress, n_clicks):
    total = 10
    for i in range(total):
        time.sleep(0.5)
        set_progress(make_progress_graph(i, 10))

    return [f"Clicked {n_clicks} times"]


if __name__ == "__main__":
    app.run_server(debug=True)
```

![](https://i.imgur.com/ACCUwbD.gif)

## Caching results with long_callback
The `long_callback` decorator can optionally [memoize](https://en.wikipedia.org/wiki/Memoization) callback function results through caching, and it provides a flexible API for configuring when cached results may be reused.

 > Note: The current caching configuration API is fairly low-level, and in the future we expect that it will be useful to provide several preconfigured caching profiles.

### How it works
Here is a high-level description of how caching works in `long_callback`. Conceptually, you can imagine a dictionary is associated with each decorated callback function.  Each time the decorated function is called, the input arguments to the function (and potentially other information about the environment) are [hashed](https://en.wikipedia.org/wiki/Hash_function) to generate a key. The `long_callback` decorator then checks the dictionary to see if there is already a value stored using this key.  If so, the decorated function is not called, and the cached result is returned.  If not, the function is called and the result is stored in the dictionary using the associated key.

The built-in [`functools.lru_cache`](https://docs.python.org/3/library/functools.html#functools.lru_cache) decorator uses a Python `dict` just like this.  The situation is slightly more complicated with Dash for two reasons:
 1. We might want the cache to persist across server restarts.
 2. When an app is served using multiple processes (e.g. multiple gunicorn workers on a single server, or multiple servers behind a load balancer), we might want to shared cached values across all of these processes. 

For these reasons, a simple Python `dict` is not a suitable storage container for caching Dash callbacks.  Instead, `long_callback` uses the current diskcache or Celery callback manager to store cached results.  

### Caching flexibility requirements
To support caching in a variety of development and production use cases, `long_callback` may be configured by one or more zero-argument functions, where the return values of these functions are combined with the function input arguments when generating the cache key.  Several common use-cases will be described below.

### Enabling caching
Caching is enabled by providing one or more zero-argument functions to the `cache_by` argument of `long_callback`.  These functions are called each time the status of a `long_callback` function is checked, and their return values are hashed as part of the cache key.    

Here is an example using the diskcache callback manager.  The `clear_cache` argument controls whether the cache is reset at startup. In this example, the `cache_by` argument is set to a `lambda` function that returns a fixed UUID that is randomly generated during app initialization. The implication of this `cache_by` function is that the cache is shared across all invocations of the callback across all user sessions that are handled by a single server instance. Each time a server process is restarted, the cache is cleared an a new UUID is generated.

```python
import time
from uuid import uuid4
import dash
import dash_html_components as html
import dash_labs as dl

## Diskcache
import diskcache
launch_uid = uuid4()
cache = diskcache.Cache("./cache")
long_callback_manager = dl.plugins.DiskcacheCachingCallbackManager(
    cache, cache_by=[lambda: launch_uid], expire=60,
)

app = dash.Dash(
    __name__,
    plugins=[
        dl.plugins.FlexibleCallbacks(),
        dl.plugins.HiddenComponents(),
        dl.plugins.LongCallback(long_callback_manager),
    ],
)

app.layout = html.Div(
    [
        html.Div([html.P(id="paragraph_id", children=["Button not clicked"])]),
        html.Button(id="button_id", children="Run Job!"),
        html.Button(id="cancel_button_id", children="Cancel Running Job!"),
    ]
)


@app.long_callback(
    output=(dl.Output("paragraph_id", "children"), dl.Output("button_id", "n_clicks")),
    args=dl.Input("button_id", "n_clicks"),
    running=[
        (dl.Output("button_id", "disabled"), True, False),
        (dl.Output("cancel_button_id", "disabled"), False, True),
    ],
    cancel=[dl.Input("cancel_button_id", "n_clicks")],
)
def callback(n_clicks):
    time.sleep(2.0)
    return [f"Clicked {n_clicks} times"], (n_clicks or 0) % 4


if __name__ == "__main__":
    app.run_server(debug=True)
```

![](https://i.imgur.com/ficfv7g.gif)

Here you can see that it takes a few seconds to run the callback function, but the cached results are used after `n_clicks` cycles back around to 0.  By interacting with the app in a separate tab, you can see that the cache results are shared across user sessions.

### cache_by function workflows
Various `cache_by` functions can be used to accomplish a variety of caching policies. Here are a few examples:
 - A `cache_by` function could return the file modification time of a dataset to automatically invalidate the cache when an input dataset changes.
 - In a Heroku or Dash Enterprise deployment setting, a `cache_by` function could return the git hash of the app, making it possible to persist the cache across redeploys, but invalidate it when the app's source changes.
 - In a Dash Enterprise setting, the `cache_by` function could return user meta-data to prevent cached values from being shared across users. 
 

## Celery configuration
Here is an example of configuring the `LongCallback` plugin to use Celery as the execution backend rather than a background process with diskcache.

```python
import dash
import dash_labs as dl
from dash_labs.plugins import CeleryCallbackManager

## Celery on RabbitMQ
from celery import Celery
celery_app = Celery(__name__, backend='rpc://', broker='pyamqp://')
long_callback_manager = CeleryCallbackManager(celery_app)

app = dash.Dash(__name__, plugins=[
    dl.plugins.FlexibleCallbacks(),
    dl.plugins.HiddenComponents(),
    dl.plugins.LongCallback(long_callback_manager)
])
```

See the [Celery documentation](https://docs.celeryproject.org/en/stable/getting-started/introduction.html) for more information on configuring a `Celery` app instance.
