import dash_express as dx
from ..fixtures import app, test_template


def test_prevent_initial_callback_passed_through(app, test_template):
    @app.callback(
        inputs=[(0, 10)],
        template=test_template,
        prevent_initial_call=False,
    )
    def fn(a, b, c):
        return a + b + c

    # False
    app._callback_list[0]["prevent_initial_call"] is False

    @app.callback(
        inputs=[(0, 10)],
        template=test_template,
        prevent_initial_call=True,
    )
    def fn(a, b, c):
        return a + b + c

    # True
    app._callback_list[1]["prevent_initial_call"] is False
