from functools import partial
from types import MethodType
import uuid


class LongCallback:
    def __init__(self, long_callback_manager):
        self.long_callback_manager = long_callback_manager

    def plug(self, app):
        self.long_callback_manager.init(app)
        app._background_procs = {}
        app._long_callback_manager = self.long_callback_manager
        app.long_callback = MethodType(partial(long_callback), app)


def long_callback(
    self,
    args,
    output,
    running=(),
    cancel=(),
    progress=(),
    progress_default=None,
    template=None,
    interval=1000,
):
    import dash
    import dash_labs as dl
    import dash_core_components as dcc
    from dash_labs.grouping import map_grouping

    callback_manager = self._long_callback_manager

    interval_id = dl.build_id("interval")
    interval_component = dcc.Interval(id=interval_id, interval=interval, disabled=True)

    user_id = str(uuid.uuid4())
    store_id = dl.build_id("store")
    store_component = dcc.Store(id=store_id, data=dict(user_id=user_id))

    cancel_prop_ids = tuple(
        ".".join([dep.component_id, dep.component_property]) for dep in cancel
    )

    # Add hidden components to app so we don't need to put them in the layout
    hidden_components = self._extra_hidden_components
    hidden_components.extend([interval_component, store_component])

    def wrapper(fn):
        background_fn = callback_manager.make_background_fn(fn, progress=bool(progress))

        def callback(n_intervals, cancel, user_store_data, user_callback_args):
            result_key = user_store_data.get("cache_result_key", None)
            if result_key is None:
                # Build result cache key from inputs
                result_key = callback_manager.build_cache_key(fn, user_callback_args)
                user_store_data["cache_result_key"] = result_key

            should_cancel = any(
                [
                    trigger["prop_id"] in cancel_prop_ids
                    for trigger in dash.callback_context.triggered
                ]
            )
            if progress_default is None:
                clear_progress = (
                    map_grouping(lambda x: None, progress.dependencies())
                    if progress
                    else ()
                )
            else:
                clear_progress = progress_default

            if should_cancel and result_key is not None:
                if callback_manager.has_future(result_key):
                    callback_manager.delete_future(result_key)
                return dict(
                    user_callback_output=map_grouping(lambda x: dash.no_update, output),
                    in_progress=tuple([val for (_, _, val) in running]),
                    progress=clear_progress,
                    interval_disabled=True,
                    user_store_data=user_store_data,
                )

            progress_value = callback_manager.get_progress(result_key)

            if callback_manager.result_ready(result_key):
                result = callback_manager.get_result(result_key)
                # Clear result key
                user_store_data["cache_result_key"] = None
                return dict(
                    user_callback_output=result,
                    in_progress=tuple([val for (_, _, val) in running]),
                    progress=clear_progress,
                    interval_disabled=True,
                    user_store_data=user_store_data,
                )
            elif progress_value:
                return dict(
                    user_callback_output=map_grouping(lambda x: dash.no_update, output),
                    in_progress=tuple([val for (_, val, _) in running]),
                    progress=progress_value or {},
                    interval_disabled=False,
                    user_store_data=user_store_data,
                )
            else:
                callback_manager.terminate_unhealthy_future(result_key)
                if not callback_manager.has_future(result_key):
                    callback_manager.call_and_register_background_fn(
                        result_key, background_fn, user_callback_args
                    )

                return dict(
                    user_callback_output=map_grouping(lambda x: dash.no_update, output),
                    in_progress=tuple([val for (_, val, _) in running]),
                    progress=clear_progress,
                    interval_disabled=False,
                    user_store_data=user_store_data,
                )

        # Add interval component to inputs
        return self.callback(
            args=dict(
                n_intervals=dl.Input(interval_id, "n_intervals"),
                cancel=tuple(dep for dep in cancel),
                user_store_data=dl.State(store_id, "data"),
                user_callback_args=args,
            ),
            output=dict(
                interval_disabled=dl.Output(interval_id, "disabled"),
                in_progress=tuple([dep for (dep, _, _) in running]),
                progress=progress,
                user_callback_output=output,
                user_store_data=dl.Output(store_id, "data"),
            ),
            template=template,
        )(callback)

    return wrapper
