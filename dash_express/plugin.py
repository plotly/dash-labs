from ._callback import _callback as dx_callback
from functools import partial
from dash import Dash
from types import MethodType

class Plugin:
    def __init__(self):
        pass

    def plug(self, app):
        print("Dash Express Plugin activated with: {}".format(app))
        _wrapped_callback = Dash.callback
        app._wrapped_callback = _wrapped_callback
        app.callback = MethodType(partial(
            dx_callback, _wrapped_callback=_wrapped_callback), app
        )
