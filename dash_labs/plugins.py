from ._callback import _callback as dx_callback
from functools import partial
from dash import Dash
from types import MethodType
import uuid
import json
from multiprocessing import Process


class FlexibleCallbacks:
    """
    Dash app plugin to enable advanced callback behaviors including:
      - Property grouping
      - Keyword argument support
      - Support for providing full components in place of ids when using the
        dl.Output/dl.Input/sl.State dependency objects.

    Usage:

    >>> import dash
    >>> import dash_labs as dl
    >>> app = dash.Dash(__name__, plugins=[dl.FlexibleCallbacks()])
    """

    def __init__(self):
        pass

    def plug(self, app):
        _wrapped_callback = Dash.callback
        app._wrapped_callback = _wrapped_callback
        app.callback = MethodType(
            partial(dx_callback, _wrapped_callback=_wrapped_callback), app
        )


class HiddenComponents:
    def plug(self, app):
        app._extra_hidden_components = []
        app._layout_value = MethodType(_layout_value, app)


def _layout_value(self):
    layout = self._layout() if self._layout_is_function else self._layout

    # Add hidden components
    if hasattr(self, "_extra_hidden_components"):
        for c in self._extra_hidden_components:
            if c not in layout.children:
                layout.children.append(c)

    return layout


class JobQueue:
    def __init__(self, cache):
        self.cache = cache

    def plug(self, app):
        self.cache.init_app(app.server)
        app._background_procs = {}
        app._flask_caching_cache = self.cache

        app.jobqueue_callback = MethodType(partial(jobqueue_callback), app)


def jobqueue_callback(self, args, output, in_progress=(), cancel=(), template=None, interval=1000):
    import dash
    import dash_labs as dl
    import dash_core_components as dcc
    from dash_labs.grouping import map_grouping

    interval_id = dl.build_id("interval")
    interval_component = dcc.Interval(
        id=interval_id, interval=interval, disabled=True
    )

    user_id = str(uuid.uuid4())
    store_id = dl.build_id("store")
    store_component = dcc.Store(
        id=store_id, data=dict(user_id=user_id)
    )

    cancel_prop_ids = tuple(".".join([component_id, component_property]) for component_id, component_property in cancel)

    # Initialize procs list on app
    procs = self._background_procs

    # Add hidden components to app so we don't need to put them in the layout
    hidden_components = self._extra_hidden_components
    hidden_components.extend([interval_component, store_component])

    def wrapper(fn):
        def callback(n_intervals, cancel, user_store_data, user_callback_args):
            print(dash.callback_context.triggered)
            if isinstance(user_callback_args, tuple):
                key = [list(user_callback_args), user_id]
            else:
                key = [user_callback_args, user_id]

            result_key = json.dumps({"args": key})

            should_cancel = any(
                [trigger["prop_id"] in cancel_prop_ids for trigger in dash.callback_context.triggered]
            )
            if should_cancel:
                if result_key in procs:
                    for proc in procs.pop(result_key):
                        proc.kill()
                return dict(
                    user_callback_output=map_grouping(
                        lambda x: dash.no_update, output
                    ),
                    in_progress=tuple([
                        val for (id, prop, _, val) in in_progress
                    ]),
                    interval_disabled=True
                )

            result = self._flask_caching_cache.get(result_key)
            if result is not None:
                if result_key in procs:
                    for proc in procs.pop(result_key):
                        proc.join()
                        proc.close()

                return dict(
                    user_callback_output=result,
                    in_progress=tuple([
                        val for (id, prop, _, val) in in_progress
                    ]),
                    interval_disabled=True
                )
            else:
                target = make_update_cache(fn, self._flask_caching_cache, result_key)
                p = Process(target=target, args=(user_callback_args,))
                p.start()
                procs.setdefault(result_key, []).append(p)

                return dict(
                    user_callback_output=map_grouping(
                        lambda x: dash.no_update, output
                    ),
                    in_progress = tuple([
                        val for (id, prop, val, _) in in_progress
                    ]),
                    interval_disabled=False,
                )

        # Add interval component to inputs
        return self.callback(
            args=dict(
                n_intervals=dl.Input(interval_id, "n_intervals"),
                cancel=tuple(dl.Input(id, prop) for id, prop in cancel),
                user_store_data=dl.Input(store_id, "data"),
                user_callback_args=args,
            ),
            output=dict(
                interval_disabled=dl.Output(interval_id, "disabled"),
                in_progress = tuple([
                    dl.Output(id, prop)
                    for (id, prop, _, _) in in_progress
                ]),
                user_callback_output=output
            ),
            template=template
        )(callback)

    return wrapper


def make_update_cache(fn, cache, result_key):
    def _callback(user_callback_args):
        if isinstance(user_callback_args, dict):
            user_callback_output = fn(**user_callback_args)
        elif isinstance(user_callback_args, (list)):
            user_callback_output = fn(*user_callback_args)
        else:
            user_callback_output = fn(user_callback_args)
        cache.set(result_key, user_callback_output)

    return _callback
