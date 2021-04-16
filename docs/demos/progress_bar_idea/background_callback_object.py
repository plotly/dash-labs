import uuid
from multiprocessing import Process

import dash
import dash_core_components as dcc
import dash_labs as dl
import json
from dash_labs.grouping import map_grouping
import dash_html_components as html


class BackgroundCallback:
    def __init__(self, app, cache, interval):
        self.app = app
        self.cache = cache
        self.interval = interval
        self.result_key = str(uuid.uuid4())
        self.result_progress = str(uuid.uuid4())

        self.interval_id = dl.build_id("interval")
        self.interval_component = dcc.Interval(id=self.interval_id, interval=interval, disabled=True)

        self.store_id = dl.build_id("store")
        self.user_id = str(uuid.uuid4())
        self.store_component = dcc.Store(
            id=self.store_id, data=dict(user_id=self.user_id)
        )

        self.loading_ids = []
        self.wrapping_ids = []
        self.procs = {}

        # Add hidden components to app so we don't need to put them in the layout
        hidden_components = getattr(app, "_extra_hidden_components", [])
        hidden_components.extend([self.interval_component, self.store_component])
        setattr(app, "_extra_hidden_components", hidden_components)

    def Loading(self, children):
        loading_id = dl.build_id("loading")
        wrapping_id = dl.build_id("wrapped")
        result = html.Div(
            id=loading_id,
            children=html.Div(id=wrapping_id, children=children)
        )
        self.loading_ids.append(loading_id)
        self.wrapping_ids.append(wrapping_id)
        return result

    def callback(self, args, output, disable=(), enable=(), cancel=(), template=None):
        cache = self.cache
        app = self.app
        interval_id = self.interval_id
        store_id = self.store_id
        loading_ids = list(self.loading_ids)
        wrapping_ids = list(self.wrapping_ids)
        user_id = self.user_id
        cancel_prop_ids = tuple(".".join([dep.component_id, dep.component_property]) for dep in cancel)

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
                    if result_key in self.procs:
                        for proc in self.procs.pop(result_key):
                            proc.kill()
                    return dict(
                        user_callback_output=map_grouping(
                            lambda x: dash.no_update, output
                        ),
                        loading_styles=tuple([
                            {"background-color": "blue", "margin": 0, "padding": 0} for _ in loading_ids
                        ]),
                        wrapping_styles=tuple([{"visibility": "visible"} for _ in wrapping_ids]),
                        disable=tuple(False for _ in disable),
                        enable=tuple(True for _ in enable),
                        interval_disabled=True
                    )

                result = cache.get(result_key)
                if result is not None:
                    if result_key in self.procs:
                        for proc in self.procs.pop(result_key):
                            proc.join()
                            proc.close()

                    return dict(
                        user_callback_output=result,
                        loading_styles=tuple([
                            {"background-color": "blue", "margin": 0, "padding": 0} for _ in loading_ids
                        ]),
                        wrapping_styles=tuple([{"visibility": "visible"} for _ in wrapping_ids]),
                        disable=tuple(False for _ in disable),
                        enable=tuple(True for _ in enable),
                        interval_disabled=True
                    )
                else:
                    target = make_update_cache(fn, cache, result_key)
                    p = Process(target=target, args=(user_callback_args,))
                    p.start()
                    self.procs.setdefault(result_key, []).append(p)
                    return dict(
                        user_callback_output=map_grouping(
                            lambda x: dash.no_update, output
                        ),
                        loading_styles=tuple([
                            {"background-color": "red", "margin": 0, "padding": 0} for c in loading_ids
                        ]),
                        wrapping_styles=tuple([{"visibility": "hidden"} for _ in wrapping_ids]),
                        disable=tuple(True for _ in disable),
                        enable=tuple(False for _ in enable),
                        interval_disabled=False,
                    )

            # Add interval component to inputs
            return app.callback(
                args=dict(
                    n_intervals=dl.Input(interval_id, "n_intervals"),
                    cancel=tuple(dep for dep in cancel),
                    user_store_data=dl.Input(store_id, "data"),
                    user_callback_args=args,
                ),
                output=dict(
                    interval_disabled=dl.Output(interval_id, "disabled"),
                    loading_styles=tuple([
                        dl.Output(loading_id, "style") for loading_id in loading_ids
                    ]),
                    wrapping_styles=tuple([
                        dl.Output(wrapping_id, "style") for wrapping_id in wrapping_ids
                    ]),
                    disable=tuple(dep for dep in disable),
                    enable=tuple(dep for dep in enable),
                    user_callback_output=output
                ),
                template=template
            )(callback)

        return wrapper


def make_update_cache(fn, cache, result_key):
    # def _set_progress(i, total):
    #     cache.set(progress_key, (i, total))

    def _callback(user_callback_args):
        if isinstance(user_callback_args, dict):
            user_callback_output = fn(**user_callback_args)
        elif isinstance(user_callback_args, (list)):
            user_callback_output = fn(*user_callback_args)
        else:
            user_callback_output = fn(user_callback_args)
        cache.set(result_key, user_callback_output)

    return _callback
