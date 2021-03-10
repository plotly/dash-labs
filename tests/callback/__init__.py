import string
from unittest.mock import MagicMock

from dash_labs import build_id
from grouping import make_grouping_by_index, grouping_len


def make_deps(dep_type, n):
    return [dep_type(build_id(), "p") for _ in range(n)]


def assert_deps_eq(deps1, deps2):
    assert isinstance(deps1, list) and isinstance(deps2, list)
    assert len(deps1) == len(deps2)
    assert all(type(d1) is type(d2) for d1, d2 in zip(deps1, deps2))
    assert all(
        d1.component_id == d2.component_id and
        d1.component_property == d2.component_property
        for d1, d2 in zip(deps1, deps2)
    )


def mock_fn_with_return(ret_val):
    mock_fn = MagicMock()
    mock_fn.return_value = ret_val
    return mock_fn


def make_letters(n, upper=False):
    letters = string.ascii_uppercase if upper else string.ascii_lowercase
    return list(letters)[:n]


def make_letters_grouping(grouping, upper=False):
    return make_grouping_by_index(
        grouping, make_letters(grouping_len(grouping), upper=upper)
    )


def make_numbers_grouping(grouping, offset=0):
    return make_grouping_by_index(
        grouping, list(range(offset, offset + grouping_len(grouping)))
    )
