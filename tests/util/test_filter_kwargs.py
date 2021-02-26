import dash_labs as dl
from dash.development.base_component import Component


def test_filter_nones_and_undefined():
    result = dl.util.filter_kwargs(
        a=12,
        b="Foo",
        c=None,
        d=["A", "B"],
        e=Component.UNDEFINED,
        f={"a": 1, "b": 2},
        g=None,
    )
    assert result == dict(a=12, b="Foo", d=["A", "B"], f={"a": 1, "b": 2})


def test_filter_args_and_kwargs():
    result = dl.util.filter_kwargs(
        dict(a=12, b="Foo", c=None),
        None,
        d=["A", "B"],
        e=Component.UNDEFINED,
        f={"a": 1, "b": 2},
        g=None,
    )
    assert result == dict(a=12, b="Foo", d=["A", "B"], f={"a": 1, "b": 2})
