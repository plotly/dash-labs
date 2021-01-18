import pytest
from collections import OrderedDict

from dash_express.util import insert_into_ordered_dict


@pytest.fixture
def odict():
    return OrderedDict()


@pytest.fixture
def full_odict():
    odict = OrderedDict()
    odict = insert_into_ordered_dict(odict, "A", key="a")
    odict = insert_into_ordered_dict(odict, "B")
    odict = insert_into_ordered_dict(odict, "C", key="c")
    return odict


def test_default_inserts(odict):
    odict = insert_into_ordered_dict(odict, "A")
    odict = insert_into_ordered_dict(odict, "B")
    odict = insert_into_ordered_dict(odict, "C")
    assert list(odict.items()) == [(0, "A"), (1, "B"), (2, "C")]


def test_default_inserts_with_keys(odict):
    odict = insert_into_ordered_dict(odict, "A", key="a")
    odict = insert_into_ordered_dict(odict, "B")
    odict = insert_into_ordered_dict(odict, "C", key="c")
    assert list(odict.items()) == [("a", "A"), (1, "B"), ("c", "C")]


def test_insert_after_by_index(full_odict):
    full_odict = insert_into_ordered_dict(full_odict, "D", key="d", after=0)
    assert list(full_odict.items()) == [("a", "A"), ("d", "D"), (2, "B"), ("c", "C")]

    full_odict = insert_into_ordered_dict(full_odict, "E", after=2)
    assert list(full_odict.items()) == [
        ("a", "A"),
        ("d", "D"),
        (2, "B"),
        (3, "E"),
        ("c", "C"),
    ]

    full_odict = insert_into_ordered_dict(full_odict, "F", after=4)
    assert list(full_odict.items()) == [
        ("a", "A"),
        ("d", "D"),
        (2, "B"),
        (3, "E"),
        ("c", "C"),
        (5, "F"),
    ]

    full_odict = insert_into_ordered_dict(full_odict, "G", key="g", after=-1)
    assert list(full_odict.items()) == [
        ("g", "G"),
        ("a", "A"),
        ("d", "D"),
        (3, "B"),
        (4, "E"),
        ("c", "C"),
        (6, "F"),
    ]


def test_insert_before_by_index(full_odict):
    full_odict = insert_into_ordered_dict(full_odict, "D", key="d", before=1)
    assert list(full_odict.items()) == [("a", "A"), ("d", "D"), (2, "B"), ("c", "C")]

    full_odict = insert_into_ordered_dict(full_odict, "E", before=3)
    assert list(full_odict.items()) == [
        ("a", "A"),
        ("d", "D"),
        (2, "B"),
        (3, "E"),
        ("c", "C"),
    ]

    full_odict = insert_into_ordered_dict(full_odict, "F", before=5)
    assert list(full_odict.items()) == [
        ("a", "A"),
        ("d", "D"),
        (2, "B"),
        (3, "E"),
        ("c", "C"),
        (5, "F"),
    ]

    full_odict = insert_into_ordered_dict(full_odict, "G", key="g", before=0)
    assert list(full_odict.items()) == [
        ("g", "G"),
        ("a", "A"),
        ("d", "D"),
        (3, "B"),
        (4, "E"),
        ("c", "C"),
        (6, "F"),
    ]


def test_insert_after_by_key(full_odict):
    full_odict = insert_into_ordered_dict(full_odict, "D", key="d", after="a")
    assert list(full_odict.items()) == [("a", "A"), ("d", "D"), (2, "B"), ("c", "C")]

    full_odict = insert_into_ordered_dict(full_odict, "E", after=2)
    assert list(full_odict.items()) == [
        ("a", "A"),
        ("d", "D"),
        (2, "B"),
        (3, "E"),
        ("c", "C"),
    ]

    full_odict = insert_into_ordered_dict(full_odict, "F", after="c")
    assert list(full_odict.items()) == [
        ("a", "A"),
        ("d", "D"),
        (2, "B"),
        (3, "E"),
        ("c", "C"),
        (5, "F"),
    ]

    full_odict = insert_into_ordered_dict(full_odict, "G", key="g", after=-1)
    assert list(full_odict.items()) == [
        ("g", "G"),
        ("a", "A"),
        ("d", "D"),
        (3, "B"),
        (4, "E"),
        ("c", "C"),
        (6, "F"),
    ]


def test_insert_before_by_key(full_odict):
    full_odict = insert_into_ordered_dict(full_odict, "D", key="d", before=1)
    assert list(full_odict.items()) == [("a", "A"), ("d", "D"), (2, "B"), ("c", "C")]

    full_odict = insert_into_ordered_dict(full_odict, "E", before="d")
    assert list(full_odict.items()) == [
        ("a", "A"),
        (1, "E"),
        ("d", "D"),
        (3, "B"),
        ("c", "C"),
    ]

    full_odict = insert_into_ordered_dict(full_odict, "F", before="c")
    assert list(full_odict.items()) == [
        ("a", "A"),
        (1, "E"),
        ("d", "D"),
        (3, "B"),
        (4, "F"),
        ("c", "C"),
    ]

    full_odict = insert_into_ordered_dict(full_odict, "G", key="g", before="a")
    assert list(full_odict.items()) == [
        ("g", "G"),
        ("a", "A"),
        (2, "E"),
        ("d", "D"),
        (4, "B"),
        (5, "F"),
        ("c", "C"),
    ]
