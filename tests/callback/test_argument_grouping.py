import pytest
import itertools

import dash_express as dx
from dash_express.grouping import make_grouping_by_position, grouping_len
from . import make_deps, assert_deps_eq, mock_fn_with_return, make_letters, \
    make_letters_grouping, make_numbers_grouping
from ..fixtures import (
    test_template, app, tuple_grouping_size, dict_grouping_size, mixed_grouping_size
)
from dash.dependencies import Input, Output, State
import dash_html_components as html

# Helpers
from ..helpers_for_testing import flat_deps

button_props = [p for p in html.Button().available_properties if p.isidentifier()]


# Tests
def test_ungrouped_positional_inputs(app, test_template):
    inputs = make_deps(Input, 2)
    state = make_deps(State, 1)
    output = make_deps(Output, 1)[0]
    @dx.callback(app, output, inputs, state, template=test_template)
    def fn(a, b, c):
        return a + b + c

    # call fn as-is
    assert fn(1, 3, 5) == 9

    # call flat version (flat version always returns a list
    assert fn._flat_fn(1, 3, 5) == [9]

    # Check order of dependencies
    assert_deps_eq(fn._flat_input_deps, inputs)
    assert_deps_eq(fn._flat_state_deps, state)
    assert_deps_eq(fn._flat_output_deps, [output])


def test_ungrouped_with_mock(app, test_template):
    inputs = make_deps(Input, 2)
    state = make_deps(State, 1)
    output = make_deps(Output, 1)[0]

    # Build mock function
    fn = mock_fn_with_return(42)
    fn_wrapper = dx.callback(app, output, inputs, state, template=test_template)(fn)

    # call flat version (like dash would)
    assert fn_wrapper._flat_fn(1, 2, 3) == [42]

    # Check how mock function was called
    args, kwargs = fn.call_args
    assert args == (1, 2, 3)
    assert not kwargs

    # Check order of dependencies
    assert_deps_eq(fn_wrapper._flat_input_deps, inputs)
    assert_deps_eq(fn_wrapper._flat_state_deps, state)
    assert_deps_eq(fn_wrapper._flat_output_deps, [output])

    args, kwargs = fn.call_args
    print(args, kwargs)


def button_component_prop_for_grouping(grouping):
    props_grouping = make_grouping_by_position(
        grouping, button_props[:grouping_len(grouping)]
    )
    return html.Button(), props_grouping


def check_component_props_as_groupings(
        app, input_grouping, state_grouping, output_grouping, template,
        input_form="list", output_form="list",
):
    # Compute grouping sizes
    input_size = grouping_len(input_grouping)
    state_size = grouping_len(state_grouping)
    output_size = grouping_len(output_grouping)

    # Make buttons
    input_button, input_prop = button_component_prop_for_grouping(input_grouping)
    state_button, state_prop = button_component_prop_for_grouping(state_grouping)
    output_button, output_prop = button_component_prop_for_grouping(output_grouping)

    # Make flat dependencies
    flat_input_deps = flat_deps(input_button, input_prop, "input") + make_deps(Input, 1)
    flat_state_deps = flat_deps(state_button, state_prop, "state")
    flat_output_deps = make_deps(Output, 1) + flat_deps(output_button, output_prop, "output")

    # Build grouped dependency lists
    grouped_input_deps = [dx.arg(input_button, props=input_prop), flat_input_deps[-1]]
    grouped_state_deps = [dx.arg(state_button, props=state_prop)]
    grouped_output_deps = [flat_output_deps[0], dx.arg(output_button, output_prop)]

    # Build flat input/output values (state is part of input now)
    flat_input_values = (
            make_letters(input_size) + ["-"] + make_letters(state_size, upper=True)
    )
    flat_output_values = [-1] + list(range(5, output_size + 5))

    # Build grouped input/output values (state is part of input)
    grouped_input_values = [
        make_letters_grouping(input_grouping), "-", make_letters_grouping(state_grouping, upper=True)
    ]
    grouped_output_values = [-1, make_numbers_grouping(output_grouping, offset=5)]

    # Handle input data forms
    if input_form == "dict":
        only_input_keys = make_letters(len(grouped_input_deps), upper=True)
        grouped_input_deps = {
            k: v for k, v in
            zip(
                only_input_keys,
                grouped_input_deps
            )
        }

        state_keys = make_letters(len(grouped_state_deps), upper=False)
        grouped_state_deps = {
            k: v for k, v in
            zip(
                state_keys,
                grouped_state_deps
            )
        }
        input_value_keys = only_input_keys + state_keys

        grouped_input_values = {
            k: v for k, v in
            zip(input_value_keys,
                grouped_input_values
            )
        }

    if output_form == "scalar":
        # Remove first extra scalar value, leave only grouped value as scalar
        grouped_output_deps = grouped_output_deps[1]
        grouped_output_values = grouped_output_values[1]
        flat_output_values = flat_output_values[1:]
        flat_output_deps = flat_output_deps[1:]
    elif output_form == "dict":
        grouped_output_deps = {
            k: v for k, v in
            zip(
                make_letters(len(grouped_output_deps), upper=True),
                grouped_output_deps
            )
        }
        grouped_output_values = {
            k: v for k, v in
            zip(
                make_letters(len(grouped_output_deps), upper=True),
                grouped_output_values
            )
        }

    # Build mock function with grouped output as return values
    fn = mock_fn_with_return(grouped_output_values)

    # Wrap callback with grouped dependency specifications
    fn_wrapper = dx.callback(
        app,
        output=grouped_output_deps,
        inputs=grouped_input_deps,
        state=grouped_state_deps,
        template=template
    )(fn)

    # call flat version (like dash.Dash.callback would)
    assert fn_wrapper._flat_fn(*flat_input_values) == flat_output_values

    # Check that mock function was called with expected grouped values
    args, kwargs = fn.call_args
    if input_form == "list":
        assert args == tuple(grouped_input_values)
        assert not kwargs
    elif input_form == "dict":
        assert kwargs == grouped_input_values
        assert not args

    # Check order of dependencies
    assert_deps_eq(fn_wrapper._flat_input_deps, flat_input_deps)
    assert_deps_eq(fn_wrapper._flat_state_deps, flat_state_deps)
    assert_deps_eq(fn_wrapper._flat_output_deps, flat_output_deps)


def check_dependencies_as_groupings(
        app, input_grouping, state_grouping, output_grouping, template,
        input_form="list", output_form="list",
):
    # Compute grouping sizes
    input_size = grouping_len(input_grouping)
    state_size = grouping_len(state_grouping)
    output_size = grouping_len(output_grouping)

    # Build flat dependency lists
    # Note we add a scalar positional argument to input and output
    flat_input_deps = make_deps(Input, input_size + 1)
    flat_state_deps = make_deps(State, state_size)
    flat_output_deps = make_deps(Output, output_size + 1)

    # Build grouped dependency lists
    grouped_input_deps = [
        make_grouping_by_position(input_grouping, flat_input_deps[:-1]),
        flat_input_deps[-1]
    ]
    grouped_state_deps = [
        make_grouping_by_position(state_grouping, flat_state_deps),
    ]
    grouped_output_deps = [
        flat_output_deps[0],
        make_grouping_by_position(output_grouping, flat_output_deps[1:])
    ]

    # Build flat input/output values (state is part of input now)
    flat_input_values = (
            make_letters(input_size) + ["-"] + make_letters(state_size, upper=True)
    )
    flat_output_values = [-1] + list(range(5, output_size + 5))

    # Build grouped input/output values (state is part of input)
    grouped_input_values = [
        make_letters_grouping(input_grouping), "-", make_letters_grouping(state_grouping, upper=True)
    ]
    grouped_output_values = [-1, make_numbers_grouping(output_grouping, offset=5)]

    if input_form == "dict":
        only_input_keys = make_letters(len(grouped_input_deps), upper=True)
        grouped_input_deps = {
            k: v for k, v in
            zip(
                only_input_keys,
                grouped_input_deps
            )
        }

        state_keys = make_letters(len(grouped_state_deps), upper=False)
        grouped_state_deps = {
            k: v for k, v in
            zip(
                state_keys,
                grouped_state_deps
            )
        }
        input_value_keys = only_input_keys + state_keys

        grouped_input_values = {
            k: v for k, v in
            zip(input_value_keys,
                grouped_input_values
            )
        }
    if output_form == "scalar":
        # Remove first extra scalar value, leave only grouped value as scalar
        grouped_output_deps = grouped_output_deps[1]
        grouped_output_values = grouped_output_values[1]
        flat_output_values = flat_output_values[1:]
        flat_output_deps = flat_output_deps[1:]
    elif output_form == "dict":
        grouped_output_deps = {
            k: v for k, v in
            zip(
                make_letters(len(grouped_output_deps), upper=True),
                grouped_output_deps
            )
        }
        grouped_output_values = {
            k: v for k, v in
            zip(
                make_letters(len(grouped_output_deps), upper=True),
                grouped_output_values
            )
        }

    # Build mock function with grouped output as return values
    fn = mock_fn_with_return(grouped_output_values)

    # Wrap callback with grouped dependency specifications
    fn_wrapper = dx.callback(
        app,
        output=grouped_output_deps,
        inputs=grouped_input_deps,
        state=grouped_state_deps,
        template=template,
    )(fn)

    # call flat version (like dash.Dash.callback would)
    assert fn_wrapper._flat_fn(*flat_input_values) == flat_output_values

    # Check that mock function was called with expected grouped values
    args, kwargs = fn.call_args
    if input_form == "list":
        assert args == tuple(grouped_input_values)
        assert not kwargs
    elif input_form == "dict":
        assert kwargs == grouped_input_values
        assert not args

    # Check order of dependencies
    assert_deps_eq(fn_wrapper._flat_input_deps, flat_input_deps)
    assert_deps_eq(fn_wrapper._flat_state_deps, flat_state_deps)
    assert_deps_eq(fn_wrapper._flat_output_deps, flat_output_deps)

# Test all combinations of fixtured groupings
@pytest.mark.parametrize("output_form", ["scalar", "list", "dict"])
@pytest.mark.parametrize("input_form", ["list", "dict"])
@pytest.mark.parametrize(
    # "ordering", list(itertools.product([0, 1, 2], repeat=3))
    "ordering", list(itertools.permutations([0, 1, 2]))
)
def test_varied_grouping_positional(
        app, tuple_grouping_size, dict_grouping_size, mixed_grouping_size,
        input_form, output_form, ordering
):
    print(input_form, output_form, ordering)

    # Unpack
    tuple_grouping, _ = tuple_grouping_size
    dict_grouping, _ = dict_grouping_size
    mixed_grouping, _ = mixed_grouping_size
    all_groupings = [tuple_grouping, dict_grouping, mixed_grouping]

    input_grouping, state_grouping, output_grouping = \
        [all_groupings[i] for i in ordering]

    check_dependencies_as_groupings(
        app, input_grouping, state_grouping, output_grouping, test_template,
        input_form=input_form, output_form=output_form
    )


# Test all combinations of fixtured groupings
@pytest.mark.parametrize("output_form", ["scalar", "list", "dict"])
@pytest.mark.parametrize("input_form", ["list", "dict"])
@pytest.mark.parametrize(
    # "ordering", list(itertools.product([0, 1, 2], repeat=3))
    "ordering", list(itertools.permutations([0, 1, 2]))
)
def test_varied_grouping_component_props(
        app, tuple_grouping_size, dict_grouping_size, mixed_grouping_size,
        test_template, input_form, output_form, ordering
):
    print(input_form, output_form, ordering)

    # Unpack
    tuple_grouping, _ = tuple_grouping_size
    dict_grouping, _ = dict_grouping_size
    mixed_grouping, _ = mixed_grouping_size
    all_groupings = [tuple_grouping, dict_grouping, mixed_grouping]

    input_grouping, state_grouping, output_grouping = \
        [all_groupings[i] for i in ordering]

    check_component_props_as_groupings(
        app, input_grouping, state_grouping, output_grouping, test_template,
        input_form=input_form, output_form=output_form
    )


def test_input_tuple_of_deps_treated_as_list(app, test_template):
    inputs = tuple(make_deps(Input, 2))
    state = tuple(make_deps(State, 1))
    output = make_deps(Output, 1)[0]

    # Build mock function
    fn = mock_fn_with_return(42)
    fn_wrapper = dx.callback(app, output, inputs, state, template=test_template)(fn)

    # call flat version (like dash would)
    assert fn_wrapper._flat_fn(1, 2, 3) == [42]

    # Check how mock function was called
    args, kwargs = fn.call_args
    assert args == (1, 2, 3)
    assert not kwargs

    # Check order of dependencies
    assert_deps_eq(fn_wrapper._flat_input_deps, list(inputs))
    assert_deps_eq(fn_wrapper._flat_state_deps, list(state))
    assert_deps_eq(fn_wrapper._flat_output_deps, [output])

    args, kwargs = fn.call_args
    print(args, kwargs)


@pytest.mark.parametrize("output_dep_form", [list, tuple])
@pytest.mark.parametrize("output_val_form", [list, tuple])
def test_output_tuple_of_deps_treated_as_list(
        app, test_template, output_dep_form, output_val_form
):
    inputs = make_deps(Input, 2)
    state = make_deps(State, 1)
    output = output_dep_form(make_deps(Output, 2))

    # Build mock function
    fn = mock_fn_with_return(output_val_form([42, 12]))
    fn_wrapper = dx.callback(app, output, inputs, state, template=test_template)(fn)

    # call flat version (like dash would)
    assert fn_wrapper._flat_fn(1, 2, 3) == [42, 12]

    # Check how mock function was called
    args, kwargs = fn.call_args
    assert args == (1, 2, 3)
    assert not kwargs

    # Check order of dependencies
    assert_deps_eq(fn_wrapper._flat_input_deps, list(inputs))
    assert_deps_eq(fn_wrapper._flat_state_deps, list(state))
    assert_deps_eq(fn_wrapper._flat_output_deps, list(output))
