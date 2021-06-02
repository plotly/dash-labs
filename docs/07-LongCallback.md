# Overview
DashLabs introduces a new callback decorator called `@long_callback`. This decorator is designed to make it easier to create callback functions that take a long time to run, without locking up the Dash app or timing out.

`@long_callback` is designed to support multiple backend executors.  Two backends are currently implemented:
 - FlaskCaching backend that runs callback logic in a separate process. This is the easiest backend to use for local development.
 - Celery backend that runs callback logic in a celery worker and returns results to the Dash app through RabbitMQ or Redis

The `@long_callback` decorator supports the same arguments as the normal `@callback` decorator, but also includes support for 3 additional arguments that will be discussion below: `running`, `cancel`, and `progress`.

## Activating Long-callback 
In Dash Labs, the long-callback functionality is activated using the `LongCallback` plugin.  To support multiple backends, the `LongCallback` plugin is, itself, configured with either a `FlaskCachingCallbackManager` or `CeleryCallbackManager` object.  Furthermore, in addition to the `LongCallback` plugin, the `FlexibleCallback` and `HiddenComponents` plugins must be enabled as well.  Here is an example of configuring an app to use the FlaskCaching backend.

```python
import dash
import dash_labs as dl

# ## FlaskCaching
from flask_caching import Cache
flask_cache = Cache(config={"CACHE_TYPE": "filesystem", "CACHE_DIR": "./cache"})
long_callback_manager = FlaskCachingCallbackManager(flask_cache)


app = dash.Dash(__name__, plugins=[
    dl.plugins.FlexibleCallbacks(),
    dl.plugins.HiddenComponents(),
    dl.plugins.LongCallback(long_callback_manager)
])
```

## Example 1: Simple background callback
Here is a simple example of using the `@long_callback` decorator to register a callback function that updates an `html.P` element with the number of times that a button has been clicked.  The callback uses `time.sleep` to simulate a long-running operation.  

```python
import time
import dash
import dash_html_components as html
import dash_labs as dl
from dash_labs.plugins import FlaskCachingCallbackManager

# ## FlaskCaching
from flask_caching import Cache
flask_cache = Cache(config={"CACHE_TYPE": "filesystem", "CACHE_DIR": "./cache"})
long_callback_manager = FlaskCachingCallbackManager(flask_cache)


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
In the previous example, there was no visual indication that the long callback was running. It was also possible to click the "Run Job!" button multiple times before the original job has the chance to complete.  This example addresses these shortcomings by disabling the button while the callback is running, and re-enabling it when the callback completes.

This is accomplished using the `running` argument to `@long_callback`.  This argument accepts a `list` of 3-element tuples.  The first element of each tuple should be an `Output` dependency object referencing a property of a component in the app layout. The second elements is the values that the property should be set to while the callback is running, and the third element is the value the property should be set to when the callback completes.

This example uses `running` to set the `disabled` property of the button to `True` while the callback is running, and `False` when it completes.

```python
import time
import dash
import dash_html_components as html
import dash_labs as dl
from dash_labs.plugins import FlaskCachingCallbackManager

# ## FlaskCaching
from flask_caching import Cache
flask_cache = Cache(config={"CACHE_TYPE": "filesystem", "CACHE_DIR": "./cache"})
long_callback_manager = FlaskCachingCallbackManager(flask_cache)

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
from dash_labs.plugins import FlaskCachingCallbackManager

# ## FlaskCaching
from flask_caching import Cache
flask_cache = Cache(config={"CACHE_TYPE": "filesystem", "CACHE_DIR": "./cache"})
long_callback_manager = FlaskCachingCallbackManager(flask_cache)

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
This example uses the `progress` argument to the `@long_callback` decorator to update a progress bar while the callback is running.  The `progress` argument should be set to an `Output` dependency object that references a tuple of two properties of a component in the app's layout. The first property will be set to the current iteration of the task that the decorated function is executing, and the second property will be set to the total number of iterations.

When a dependency object is assigned to the `progress` argument of `@long_callback`, the decorated function will be called with a new special argument as the first argument to the function.  This special argument, named `set_progress` in the example below, is a function handle that the decorated function should call in order to provide updates to the app on its current progress.  The `set_progress` function accepts two positional argument, which correspond to the two properties specified in the `Output` dependency object passed to the `progress` argument of `@long_callback`.  The first argument to `set_progress` should be the current iteration of the task that the decorated function is executing, and the second argument should be the total number of iterations.

```python
import time
import dash
import dash_html_components as html
import dash_labs as dl
from dash_labs.plugins import FlaskCachingCallbackManager, CeleryCallbackManager

# ## FlaskCaching
from flask_caching import Cache
flask_cache = Cache(config={"CACHE_TYPE": "filesystem", "CACHE_DIR": "./cache"})
long_callback_manager = FlaskCachingCallbackManager(flask_cache)

# ## FlaskCaching
flask_cache = Cache(config={"CACHE_TYPE": "filesystem", "CACHE_DIR": "./cache"})
long_callback_manager = FlaskCachingCallbackManager(flask_cache)

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
        set_progress(str(i + 1), str(total))
    # Set progress back to indeterminate state for next time
    set_progress(None, None)
    return [f"Clicked {n_clicks} times"]


if __name__ == "__main__":
    app.run_server(debug=True)
```

![](https://i.imgur.com/0tRGCH8.gif)

## Celery configuration
Here is an example of configuring the `LongCallback` plugin to use Celery as the execution backend rather than a background process with FlaskCaching.

```python
import dash
import dash_labs as dl
from dash_labs.plugins import CeleryCallbackManager, FlaskCachingCallbackManager

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
