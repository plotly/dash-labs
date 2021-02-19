import dash_express as dx
from multiprocessing import Process
import dash_html_components as html
import dash_core_components as dcc
import json
from dash.dependencies import Output


# User defined
def background_callback(app, cache, inputs, interval=1000):
    progress_id = dx.build_id("progress")
    progress_style = {"width": "100%"}
    def wrapper(fn):
        def callback(__n_intervals__, *args, **kwargs):
            result_key = json.dumps({"args": list(args), "kwargs": kwargs})
            progress_key = result_key + "-progress"
            result = cache.get(result_key)
            progress = cache.get(progress_key)
            if result is not None:
                return dict(
                    result=result,
                    interval_disabled=True
                )
            elif progress is not None:
                return dict(
                    result=html.Progress(
                        value=str(progress[0]), max=str(progress[1]), id=progress_id, style=progress_style
                    ),
                    interval_disabled=False
                )
            else:
                target = make_update_cache(fn, cache, result_key, progress_key)
                p = Process(target=target, args=args, kwargs=kwargs)
                p.start()
                return dict(
                    result=html.Progress(id=progress_id, style=progress_style),
                    interval_disabled=False
                )
        interval_component = dx.arg(
            dcc.Interval(interval=interval, id=dx.build_id("interval")),
            props="n_intervals", label=None,
        )

        # Add interval component to inputs
        all_inputs = inputs
        if isinstance(all_inputs, dict):
            all_inputs = dict(all_inputs, __n_intervals__=interval_component)
        else:
            if not isinstance(all_inputs, (list, tuple)):
                all_inputs = [all_inputs]
            all_inputs = [interval_component] + all_inputs

        all_output = dict(
            result=dx.arg(html.Div(), props="children"),
            interval_disabled=Output(interval_component.id, "disabled")
        )
        return app.callback(inputs=all_inputs, output=all_output)(callback)

    return wrapper


def make_update_cache(callback, cache, result_key, progress_key):
    def _set_progress(i, total):
        cache.set(progress_key, (i, total))

    def _callback(*args, **kwargs):
        result = callback(_set_progress, *args, **kwargs)
        cache.set(result_key, result)

    return _callback
