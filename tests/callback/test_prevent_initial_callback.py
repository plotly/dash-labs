import dash_express as dx
from unittest.mock import MagicMock

from ..fixtures import test_template


def test_prevent_initial_callback_passed_through(test_template):
    app = MagicMock()
    @dx.callback(
        app,
        inputs=[(0, 10)],
        template=test_template,
        prevent_initial_call=False,
    )
    def fn(a, b, c):
        return a + b + c

    # False
    args = app.callback.call_args
    assert not args.kwargs.get("prevent_initial_call", False)

    @dx.callback(
        app,
        inputs=[(0, 10)],
        template=test_template,
        prevent_initial_call=True,
    )
    def fn(a, b, c):
        return a + b + c

    # True
    args = app.callback.call_args
    assert args.kwargs["prevent_initial_call"]
