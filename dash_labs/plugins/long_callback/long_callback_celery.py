from functools import partial
from types import MethodType
import uuid
import json
import celery
from multiprocessing import Process


class LongCallbackCelery:
    def __init__(self, celery_app):
        self.long_callback_manager = CeleryCallbackManager(celery_app)

    def plug(self, app):
        # self.cache.init_app(app.server)
        app._background_procs = {}
        app._long_callback_manager = self.long_callback_manager
        app.long_callback = MethodType(partial(long_callback), app)



class CeleryCallbackManager:
    def __init__(self, celery_app):
        self.celery_app = celery_app
        self.callback_futures = dict()

    def cancel_future(self, key):
        if key in self.callback_futures:
            future = self.callback_futures[key]
            self.celery_app.control.terminate(future.task_id)
            return True
        return False

    def terminate_unhealthy_future(self, key):
        if key in self.callback_futures:
            future = self.callback_futures[key]
            if future.status != "PENDING":
                return self.cancel_future(key)
        return False

    def has_future(self, key):
        return key in self.callback_futures

    def get_future(self, key, default=None):
        return self.callback_futures.get(key, default)

    def make_background_fn(self, fn, progress=False):
        return make_celery_fn(fn, self.celery_app, progress)

    def call_and_register_background_fn(self, key, delayed, *args, **kwargs):
        future = delayed.delay(*args, **kwargs)
        self.callback_futures[key] = future

    def get_progress(self, key):
        future = self.get_future(key)
        if future is not None:
            progress_info = future.info if future.state == "PROGRESS" else None
            if progress_info is not None:
                return (
                    progress_info["current"],
                    progress_info["total"]
                )
        return None

    def result_ready(self, key):
        future = self.get_future(key)
        if future:
            return future.ready()
        else:
            return False

    def get_result(self, key):
        future = self.get_future(key)
        if future:
            return future.get(timeout=1)
        else:
            return None


def make_celery_fn(user_fn, celery_app, progress):
    @celery_app.task(bind=True)
    def _celery_fn(self, user_callback_args):
        def _set_progress(i, total):
            self.update_state(state="PROGRESS", meta={'current': i, 'total': total})

        maybe_progress = [_set_progress] if progress else []
        print(maybe_progress)

        if isinstance(user_callback_args, dict):
            user_callback_output = user_fn(*maybe_progress, **user_callback_args)
        elif isinstance(user_callback_args, list):
            user_callback_output = user_fn(*maybe_progress, *user_callback_args)
        else:
            user_callback_output = user_fn(*maybe_progress, user_callback_args)
        return user_callback_output
    return _celery_fn


def long_callback(self, args, output, running=(), cancel=(), progress=(), template=None, interval=1000):
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

    cancel_prop_ids = tuple(".".join([dep.component_id, dep.component_property]) for dep in cancel)

    callback_manager: CeleryCallbackManager = self._long_callback_manager

    # Add hidden components to app so we don't need to put them in the layout
    hidden_components = self._extra_hidden_components
    hidden_components.extend([interval_component, store_component])

    def wrapper(fn):

        # Make and register celery function
        background_fn = callback_manager.make_background_fn(fn, progress)

        def callback(n_intervals, cancel, user_store_data, user_callback_args):
            if isinstance(user_callback_args, tuple):
                key = [list(user_callback_args), user_id]
            else:
                key = [user_callback_args, user_id]

            result_key = json.dumps({"args": key})

            should_cancel = any(
                [trigger["prop_id"] in cancel_prop_ids for trigger in dash.callback_context.triggered]
            )
            clear_progress = map_grouping(
                        lambda x: None, progress.dependencies()
            ) if progress else ()

            if should_cancel:
                if callback_manager.has_future(result_key):
                    callback_manager.cancel_future(result_key)
                return dict(
                    user_callback_output=map_grouping(
                        lambda x: dash.no_update, output.dependencies()
                    ),
                    in_progress=tuple([
                        val for (_, _, val) in running
                    ]),
                    progress=clear_progress,
                    interval_disabled=True
                )

            progress_tuple = callback_manager.get_progress(result_key)

            if callback_manager.result_ready(result_key):
                result = callback_manager.get_result(result_key)
                return dict(
                    user_callback_output=result,
                    in_progress=tuple([
                        val for (_, _, val) in running
                    ]),
                    progress=clear_progress,
                    interval_disabled=True,
                )
            elif progress_tuple:
                return dict(
                    user_callback_output=map_grouping(
                        lambda x: dash.no_update, output.dependencies()
                    ),
                    in_progress=tuple([
                        val for (_, val, _) in running
                    ]),
                    progress=progress_tuple,
                    interval_disabled=False,
                )
            else:
                callback_manager.terminate_unhealthy_future(result_key)
                if not callback_manager.has_future(result_key):
                    callback_manager.call_and_register_background_fn(result_key, background_fn, user_callback_args)

                return dict(
                    user_callback_output=map_grouping(
                        lambda x: dash.no_update, output.dependencies()
                    ),
                    in_progress=tuple([
                        val for (_, val, _) in running
                    ]),
                    progress=clear_progress,
                    interval_disabled=False,
                )

        # Add interval component to inputs
        return self.callback(
            args=dict(
                n_intervals=dl.Input(interval_id, "n_intervals"),
                cancel=tuple(dep for dep in cancel),
                user_store_data=dl.Input(store_id, "data"),
                user_callback_args=args,
            ),
            output=dict(
                interval_disabled=dl.Output(interval_id, "disabled"),
                in_progress=tuple([
                    dep
                    for (dep, _, _) in running
                ]),
                progress=progress,
                user_callback_output=output
            ),
            template=template
        )(callback)

    return wrapper
