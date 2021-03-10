from collections import namedtuple
from dash.dependencies import Input
from dash_labs.grouping import (
    flatten_grouping,
    make_grouping_by_index,
    grouping_len,
    make_grouping_by_key,
    make_grouping_by_attr,
    map_grouping,
    make_schema_with_nones,
    validate_grouping,
    SchemaTypeValidationError,
    SchemaLengthValidationError,
    SchemaKeysValidationError,
)

from ..fixtures import *


# Test flatten_grouping and grouping_len
def test_flatten_scalar(scalar_grouping_size):
    grouping, size = scalar_grouping_size
    expected = list(range(size))
    result = flatten_grouping(grouping)
    assert expected == result
    assert len(result) == grouping_len(grouping)


def test_flatten_tuple(tuple_grouping_size):
    grouping, size = tuple_grouping_size
    expected = list(range(size))
    result = flatten_grouping(grouping)
    assert expected == result
    assert len(result) == grouping_len(grouping)


def test_flatten_dict(dict_grouping_size):
    grouping, size = dict_grouping_size
    expected = list(range(size))
    result = flatten_grouping(grouping)
    assert expected == result
    assert len(result) == grouping_len(grouping)


def test_flatten_mixed(mixed_grouping_size):
    grouping, size = mixed_grouping_size
    expected = list(range(size))
    result = flatten_grouping(grouping)
    assert expected == result
    assert len(result) == grouping_len(grouping)


def test_flatten_odd_value():
    # Anything other than tuple and dict should be treated as a
    # scalar and passed through
    expected = [0, sum, Input("foo", "bar")]
    vals_collection = (0, (sum, Input("foo", "bar")))
    result = flatten_grouping(vals_collection)
    assert expected == result
    assert len(result) == grouping_len(vals_collection)


# Test make_grouping_by_position
def make_flat_values(size):
    return list(string.ascii_lowercase[:size])


def test_make_grouping_by_position_scalar(scalar_grouping_size):
    grouping, size = scalar_grouping_size
    flat_values = make_flat_values(size)
    result = make_grouping_by_index(grouping, flat_values)
    expected = flat_values[0]
    assert expected == result


def test_make_grouping_by_position_tuple(tuple_grouping_size):
    grouping, size = tuple_grouping_size
    flat_values = make_flat_values(size)
    result = make_grouping_by_index(grouping, flat_values)
    expected = tuple(flat_values)
    assert expected == result


def test_make_grouping_by_position_dict(dict_grouping_size):
    grouping, size = dict_grouping_size
    flat_values = make_flat_values(size)
    result = make_grouping_by_index(grouping, flat_values)
    expected = {k: flat_values[i] for i, k in enumerate(grouping)}
    assert expected == result


def test_make_grouping_by_position_mixed(mixed_grouping_size):
    grouping, size = mixed_grouping_size
    flat_values = make_flat_values(size)
    result = make_grouping_by_index(grouping, flat_values)

    # Check for size mutation on flat_values
    assert len(flat_values) == size

    # Check with stack-based algorithm as independent implementation
    groupings = [grouping]
    results = [result]
    while groupings:
        next_grouping = groupings.pop(0)
        next_result = results.pop(0)
        print("check {} with {}".format(next_result, next_grouping))
        if isinstance(next_grouping, tuple):
            assert isinstance(next_result, tuple)
            assert len(next_grouping) == len(next_result)
            groupings.extend(next_grouping)
            results.extend(next_result)
        elif isinstance(next_grouping, dict):
            assert isinstance(next_result, dict)
            assert list(next_result) == list(next_grouping)
            groupings.extend(next_grouping.values())
            results.extend(next_result.values())
        else:
            assert isinstance(next_grouping, int)
            assert flat_values[next_grouping] == next_result


# Test make_grouping_by_key
def make_key_source(size):
    return {i: string.ascii_lowercase[i] for i in range(size)}


def test_make_grouping_by_key_scalar(scalar_grouping_size):
    grouping, size = scalar_grouping_size
    source = make_key_source(size)
    result = make_grouping_by_key(grouping, source)
    expected = source[0]
    print(grouping, source, result)
    assert expected == result


def test_make_grouping_by_key_tuple(tuple_grouping_size):
    grouping, size = tuple_grouping_size
    source = make_key_source(size)
    result = make_grouping_by_key(grouping, source)
    expected = tuple(source[i] for i in range(size))
    assert expected == result


def test_make_grouping_by_key_dict(dict_grouping_size):
    grouping, size = dict_grouping_size
    source = make_key_source(size)
    result = make_grouping_by_key(grouping, source)
    expected = {k: source[v] for k, v in grouping.items()}
    assert expected == result


def test_make_grouping_by_key_mixed(mixed_grouping_size):
    grouping, size = mixed_grouping_size
    source = {i: string.ascii_lowercase[i] for i in range(size)}
    result = make_grouping_by_key(grouping, source)

    # Check with stack-based algorithm as independent implementation
    groupings = [grouping]
    results = [result]
    while groupings:
        next_grouping = groupings.pop(0)
        next_result = results.pop(0)
        print("check {} with {}".format(next_result, next_grouping))
        if isinstance(next_grouping, tuple):
            assert isinstance(next_result, tuple)
            assert len(next_grouping) == len(next_result)
            groupings.extend(next_grouping)
            results.extend(next_result)
        elif isinstance(next_grouping, dict):
            assert isinstance(next_result, dict)
            assert list(next_result) == list(next_grouping)
            groupings.extend(next_grouping.values())
            results.extend(next_result.values())
        else:
            assert source[next_grouping] == next_result


def test_make_grouping_by_key_default():
    grouping = (0, {"A": 1, "B": 2})
    source = make_key_source(2)
    result = make_grouping_by_key(grouping, source)
    expected = ("a", {"A": "b", "B": None})
    assert expected == result

    # Custom default
    result = make_grouping_by_key(grouping, source, default="_missing_")
    expected = ("a", {"A": "b", "B": "_missing_"})
    assert expected == result


# Test make_grouping_by_attr
def make_grouping_attr_source(int_grouping):
    size = grouping_len(int_grouping)
    props = make_flat_values(size)
    vals = list(range(100, 100 + size))
    letter_grouping = make_grouping_by_index(int_grouping, props)
    Source = namedtuple("Source", props)
    return letter_grouping, Source(*vals)


def test_make_grouping_by_attr_scalar(scalar_grouping_size):
    int_grouping, size = scalar_grouping_size
    letter_grouping, source = make_grouping_attr_source(int_grouping)
    result = make_grouping_by_attr(letter_grouping, source)
    expected = getattr(source, flatten_grouping(letter_grouping)[0])
    assert expected == result


def test_make_grouping_by_attr_tuple(tuple_grouping_size):
    int_grouping, size = tuple_grouping_size
    letter_grouping, source = make_grouping_attr_source(int_grouping)
    result = make_grouping_by_attr(letter_grouping, source)
    flat_props = flatten_grouping(letter_grouping)
    expected = tuple(getattr(source, p) for p in flat_props)
    assert expected == result


def test_make_grouping_by_attr_dict(dict_grouping_size):
    int_grouping, size = dict_grouping_size
    letter_grouping, source = make_grouping_attr_source(int_grouping)
    result = make_grouping_by_attr(letter_grouping, source)
    expected = {k: getattr(source, v) for k, v in letter_grouping.items()}
    assert expected == result


def test_make_grouping_by_attr_mixed(mixed_grouping_size):
    int_grouping, size = mixed_grouping_size
    letter_grouping, source = make_grouping_attr_source(int_grouping)
    result = make_grouping_by_attr(letter_grouping, source)

    # Check with stack-based algorithm as independent implementation
    groupings = [letter_grouping]
    results = [result]
    while groupings:
        next_grouping = groupings.pop(0)
        next_result = results.pop(0)
        print("check {} with {}".format(next_result, next_grouping))
        if isinstance(next_grouping, tuple):
            assert isinstance(next_result, tuple)
            assert len(next_grouping) == len(next_result)
            groupings.extend(next_grouping)
            results.extend(next_result)
        elif isinstance(next_grouping, dict):
            assert isinstance(next_result, dict)
            assert list(next_result) == list(next_grouping)
            groupings.extend(next_grouping.values())
            results.extend(next_result.values())
        else:
            assert getattr(source, next_grouping) == next_result


def test_make_grouping_by_attr_default():
    letter_grouping = ("a", {"A": "b", "B": "c"})
    Source = namedtuple("Source", ["a", "c"])
    source = Source(100, 101)

    result = make_grouping_by_attr(letter_grouping, source)
    expected = (100, {"A": None, "B": 101})
    assert expected == result

    # Custom default
    result = make_grouping_by_attr(letter_grouping, source, default=-1)
    expected = (100, {"A": -1, "B": 101})
    assert expected == result


def test_map_grouping_scalar(scalar_grouping_size):
    grouping, size = scalar_grouping_size
    result = map_grouping(lambda x: x * 2 + 5, grouping)
    expected = grouping * 2 + 5
    assert expected == result


# Test map_grouping
def test_map_grouping_tuple(tuple_grouping_size):
    grouping, size = tuple_grouping_size
    result = map_grouping(lambda x: x * 2 + 5, grouping)
    expected = tuple(g * 2 + 5 for g in grouping)
    assert expected == result


def test_map_grouping_dict(dict_grouping_size):
    grouping, size = dict_grouping_size
    result = map_grouping(lambda x: x * 2 + 5, grouping)
    expected = {k: v * 2 + 5 for k, v in grouping.items()}
    assert expected == result


def test_map_grouping_mixed(mixed_grouping_size):
    grouping, size = mixed_grouping_size
    def fn(x): return x*2 + 5
    result = map_grouping(fn, grouping)
    expected = make_grouping_by_index(
        grouping, list(map(fn, flatten_grouping(grouping)))
    )
    assert expected == result


# Test make_schema
def test_make_schema_mixed(mixed_grouping_size):
    grouping, size = mixed_grouping_size
    result = make_schema_with_nones(grouping)
    expected = make_grouping_by_index(
        grouping, [None for _ in range(grouping_len(grouping))]
    )
    assert expected == result


# Test validate_schema
def test_validate_schema_grouping_scalar(scalar_grouping_size):
    grouping, size = scalar_grouping_size
    schema = make_schema_with_nones(grouping)
    validate_grouping(grouping, schema)

    # Anything is valid as a scalar
    validate_grouping((0,), schema)
    validate_grouping({"a": 0}, schema)

def test_validate_schema_grouping_tuple(tuple_grouping_size):
    grouping, size = tuple_grouping_size
    schema = make_schema_with_nones(grouping)
    validate_grouping(grouping, schema)

    # check validation failures
    with pytest.raises(SchemaTypeValidationError):
        validate_grouping(None, schema)

    with pytest.raises(SchemaLengthValidationError):
        validate_grouping((None,)*(size + 1), schema)

    with pytest.raises(SchemaTypeValidationError):
        validate_grouping({"a": 0}, schema)


def test_validate_schema_dict(dict_grouping_size):
    grouping, size = dict_grouping_size
    schema = make_schema_with_nones(grouping)
    validate_grouping(grouping, schema)

    # check validation failures
    with pytest.raises(SchemaTypeValidationError):
        validate_grouping(None, schema)

    with pytest.raises(SchemaTypeValidationError):
        validate_grouping((None,), schema)

    with pytest.raises(SchemaKeysValidationError):
        validate_grouping({"A": 0, "bogus": 2}, schema)


def test_validate_schema_mixed(mixed_grouping_size):
    grouping, size = mixed_grouping_size
    schema = make_schema_with_nones(grouping)
    validate_grouping(grouping, schema)

    # check validation failures
    with pytest.raises(SchemaTypeValidationError):
        validate_grouping(None, schema)

    # Check invalid tuple value
    if isinstance(schema, tuple):
        err = SchemaLengthValidationError
    else:
        err = SchemaTypeValidationError
    with pytest.raises(err):
        validate_grouping((None,), schema)

    # Check invalid dict value
    if isinstance(schema, dict):
        err = SchemaKeysValidationError
    else:
        err = SchemaTypeValidationError

    with pytest.raises(err):
        validate_grouping({"A": 0, "bogus": 2}, schema)
