import uuid
import random
from collections import OrderedDict

from dash.development.base_component import Component
import re


def reset_uid_random_seed(seed=0):
    random.seed(seed)


reset_uid_random_seed()


def build_id(name=None, **kwargs):
    uid = str(uuid.UUID(int=random.randint(0, 2 ** 128)))
    return dict(
        uid=uid,
        **filter_kwargs(name=name, **kwargs),
    )


def filter_kwargs(**kwargs):
    return {
        k: v
        for k, v in kwargs.items()
        if v is not None and v is not Component.UNDEFINED
    }


def insert_into_ordered_dict(odict, value, key=None, before=None, after=None):
    """
    Return copy of input OrderedDict with value inserted at a specific location.

    Does not modify input OrderedDict

    If key is specified, it must be a string and it must not already be present as a key
    in the input OrderedDict. It will be used as the key corresponding
    to the provided value in the resulting OrderedDict.  If None, the key will be
    the integer index of the insertion location.

    before and after may be strings or integer indices
    """
    # Validation
    if key is not None:
        if not isinstance(key, str):
            raise ValueError("key argument must be a string or None")
        if key in odict:
            raise ValueError("Provided key already present in dictionary")

    if before is not None and after is not None:
        raise ValueError("before and after may not both be specified")

    keys = list(odict)
    if before is None and after is None:
        insert_index = len(odict)
    elif before is not None:
        if isinstance(before, int):
            before_index = before
        else:
            before_index = keys.index(before)
        insert_index = before_index
    else:  # after is not None:
        if isinstance(after, int):
            after_index = after
        else:
            after_index = keys.index(after)
        insert_index = after_index + 1

    # User insert index as name if none provided
    if key is None:
        key = insert_index

    items = list(odict.items())
    items.insert(insert_index, (key, value))

    # Replace all integer names with index to avoid overwriting
    items = [(k if isinstance(k, str) else i, v) for i, (k, v) in enumerate(items)]
    return OrderedDict(items)


def add_css_class(component, className):
    if not className:
        return

    if isinstance(className, list):
        # Join list to string for uniform processing below
        className = " ".join(className)
    elif not isinstance(className, str):
        raise ValueError(
            "className must be a string, but received value of type {typ}".format(
                typ=type(className)
            )
        )

    def normalize_and_split(classes_str):
        if not classes_str:
            return []

        classes_str = classes_str.strip()
        if not classes_str:
            return []

        classes_str = re.sub(r"\s+", " ", classes_str)
        return classes_str.split(" ")

    existing_classes = normalize_and_split(getattr(component, "className", None))
    new_classes = [
        cn for cn in normalize_and_split(className) if cn not in existing_classes
    ]
    all_classes = existing_classes + new_classes
    if new_classes is None:
        return
    else:
        component.className = " ".join(all_classes)
