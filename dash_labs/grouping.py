def flatten_grouping(grouping, schema=None):
    if schema is None:
        schema = grouping

    if isinstance(schema, tuple):
        return [
            g for group_el, schema_el in zip(grouping, schema)
            for g in flatten_grouping(group_el, schema_el)
        ]
    elif isinstance(schema, dict):
        return [g for group_el in grouping.values() for g in flatten_grouping(group_el)]
    else:
        return [grouping]


def grouping_len(grouping, schema=None):
    if schema is None:
        schema = grouping

    if isinstance(schema, tuple):
        return sum([
            grouping_len(group_el, schema_el)
            for group_el, schema_el in zip(grouping, schema)
        ])
    elif isinstance(schema, dict):
        return sum([
            grouping_len(group_el, schema_el)
            for group_el, schema_el in zip(grouping.values(), schema.values())
        ])
    else:
        return 1


def make_grouping_by_position(grouping, flat_values):
    """
    Make grouping like grouping using traversal index. Values in grouping are not
    used
    """

    def _perform_make_grouping_like(value, next_values):
        if isinstance(value, tuple):
            return tuple(
                _perform_make_grouping_like(el, next_values)
                for i, el in enumerate(value)
            )
        elif isinstance(value, dict):
            return {
                k: _perform_make_grouping_like(v, next_values)
                for i, (k, v) in enumerate(value.items())
            }
        else:
            return next_values.pop(0)

    if not isinstance(flat_values, list):
        raise ValueError(
            "The flat_values argument must be a list. "
            "Received value of type {typ}".format(typ=type(flat_values))
        )

    expected_length = len(flatten_grouping(grouping))
    if len(flat_values) != expected_length:
        raise ValueError(
            "The specified grouping pattern requires {n} elements but received {m}\n"
            "    Grouping patter: {pattern}\n"
            "    Values: {flat_values}".format(
                n=expected_length,
                m=len(flat_values),
                pattern=repr(grouping),
                flat_values=flat_values,
            )
        )

    return _perform_make_grouping_like(grouping, list(flat_values))


def _make_grouping_by_getter(grouping, source, default, getter):
    if isinstance(grouping, tuple):
        return tuple(
            _make_grouping_by_getter(g, source, default, getter) for g in grouping
        )
    elif isinstance(grouping, dict):
        return {
            k: _make_grouping_by_getter(g, source, default, getter)
            for k, g in grouping.items()
        }
    else:
        return getter(source, grouping, default)


def make_grouping_by_attr(grouping, source, default=None):
    return _make_grouping_by_getter(grouping, source, default, getattr)


def make_grouping_by_key(grouping, source, default=None):
    return _make_grouping_by_getter(grouping, source, default, type(source).get)


def map_grouping(fn, grouping):
    if isinstance(grouping, tuple):
        return tuple(
            map_grouping(fn, g) for g in grouping
        )
    elif isinstance(grouping, dict):
        return {k: map_grouping(fn, g) for k, g in grouping.items()}
    else:
        return fn(grouping)


def make_schema(grouping):
    """
    Replace all leaf values with None
    """
    return map_grouping(lambda _: None, grouping)


class SchemaValidationError(ValueError):
    pass


def validate_grouping(grouping, schema, allow_scalar_dict=False):
    def check(condition):
        if not condition:
            raise SchemaValidationError()

    if isinstance(schema, tuple):
        check(isinstance(grouping, tuple))
        check(len(grouping) == len(schema))
        for g, s in zip(grouping, schema):
            validate_grouping(g, s)
    elif isinstance(schema, dict):
        check(isinstance(grouping, dict))
        check(set(grouping) == set(schema))
        for k in schema:
            validate_grouping(grouping[k], schema[k])
    else:
        invalid = (tuple,) + (dict,) if not allow_scalar_dict else ()
        check(not isinstance(grouping, invalid))
