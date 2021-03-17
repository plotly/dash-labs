import dash_labs as dl
from multiprocessing import Process
import dash_html_components as html
import dash_core_components as dcc
import json
from dash.dependencies import Output


# User defined
def background_callback(app, cache, args, output=None, interval=1000, template=None):
    progress_id = dl.build_id("progress")
    progress_style = {"width": "100%"}

    def wrapper(fn):
        def callback(__n_intervals__, *args, **kwargs):
            result_key = json.dumps({"args": list(args), "kwargs": kwargs})
            progress_key = result_key + "-progress"
            result = cache.get(result_key)
            progress = cache.get(progress_key)
            if result is not None:
                return dict(result=result, interval_disabled=True)
            elif progress is not None:
                return dict(
                    result=html.Progress(
                        value=str(progress[0]),
                        max=str(progress[1]),
                        id=progress_id,
                        style=progress_style,
                    ),
                    interval_disabled=False,
                )
            else:
                target = make_update_cache(fn, cache, result_key, progress_key)
                p = Process(target=target, args=args, kwargs=kwargs)
                p.start()
                return dict(
                    result=html.Progress(id=progress_id, style=progress_style),
                    interval_disabled=False,
                )

        interval_component = dl.Input(
            dcc.Interval(interval=interval, id=dl.build_id("interval")),
            "n_intervals",
            label=None,
        )

        # Add interval component to inputs
        all_args = args
        if isinstance(all_args, dict):
            all_args = dict(all_args, __n_intervals__=interval_component)
        else:
            if not isinstance(all_args, (list, tuple)):
                all_args = [all_args]
            all_args = [interval_component] + all_args

        all_output = dict(
            result=dl.Output(html.Div(), "children"),
            interval_disabled=Output(interval_component.id, "disabled"),
        )
        return app.callback(args=all_args, output=all_output, template=template)(
            callback
        )

    return wrapper


def make_update_cache(callback, cache, result_key, progress_key):
    def _set_progress(i, total):
        cache.set(progress_key, (i, total))

    def _callback(*args, **kwargs):
        result = callback(_set_progress, *args, **kwargs)
        cache.set(result_key, result)

    return _callback
