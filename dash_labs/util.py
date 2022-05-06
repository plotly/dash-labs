import uuid
import random
from collections import OrderedDict
import pprint
import re
import dash
from dash.development.base_component import Component


# Create dedicated random number generator for build UUIDs
_uid_random = random.Random(0)


def _reset_uuid_random_seed(seed=0):
    """
    Reset the random seed used to generate the UUID strings added to the component
    id values produced by the build_id function.

    :param seed: New random seed
    :type seed: int
    """
    _uid_random.seed(seed)


def build_id(name=None, **kwargs):
    """
    Build a unique component id. The returned id is a dictionary containing
    a UUID string as the value of a `uid` key. If the name and/or kwargs arguments are
    provided, these will be added to the returned dictionary as well.

    The UUID strings are generated using a fixed random seed so their values are
    deterministic across multiple executions of an app, and multiple processes running
    the same app.
    """
    uid = str(uuid.UUID(int=_uid_random.randint(0, 2**128)))
    return dict(
        uid=uid,
        **filter_kwargs(name=name, **kwargs),
    )


def filter_kwargs(*args, **kwargs):
    """
    Combine dictionaries and remove values that are None or Component.UNDEFINED

    :param args: List of dictionaries with string keys to filter
    :param kwargs: Additional keyword arguments to filter
    :return: dict containing all of the key-value pairs from args and kwargs with
        values that are not None and not Component.UNDEFINED
    """
    result = {}

    for arg in list(args) + [kwargs]:
        if isinstance(arg, dict):
            for k, v in arg.items():
                if v is not None and v is not Component.UNDEFINED:
                    result[k] = v

    return result


def insert_into_ordered_dict(odict, value, key=None, before=None, after=None):
    """
    Return copy of the input OrderedDict with a value inserted at a specific location.

    Does not modify input OrderedDict

    If key is specified, it must be a string and it must not already be present as a key
    in the input OrderedDict. It will be used as the key corresponding
    to the provided value in the resulting OrderedDict.  If None, the key will be
    the integer index of the insertion location.

    before and after may be strings or integer indices and they can be set the value
    of an existing key in the OrderedDict that the new value should be instered before
    or after.
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
    """
    Update the className property of a Dash component to include a CSS class name.
    If one or more classes already exist, the provided className will  be appended
    to the list. If the provided className is already present, no change will be made
    to the component.

    Note: This function mutates the provided component's className property in-place.

    :param component: Dash component
    :param className: CSS class name string
    """
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


def print_registry(modules="ALL", exclude=None, include="ALL"):
    """
    Debugging tool and pretty printer for dash.page_registry. Prints to the console.
    Note that if `print_registry()` is called from a file in the `pages` folder, the `dash.page_registry`
    may not be complete.

    :param modules: (string or list) Default "ALL".  Specifies which modules to print.
    :param exclude: (string or list) Default None.   Specifies which of the page's  parameter(s) to exclude.
    :param include: (string or list) Default "ALL".  Prints only the parameters that are specified.

    Examples:

    - `print_registry()`  Will print the entire content of dash.page_registry
    - `print_registry("pages.home")` will print only one module
    - `print_registry(__name__)`  will print the current module.  If it's run from app.py it will print all modules
    - `print_registry(["pages.home", "pages.archive"])` Will print 2 modules
    - `print_registry(exclude="layout")`  will print info for all the modules, but will exclude the page["layout"]
    - `print_registry(include=["path", "name"]` will print only the page["path"] and page["name"] for all modules
    - `print_registry(exclude="ALL") prints the keys (module names) only
    - `print_registry(include=None) prints the keys (module names) only

    """
    print(
        '**Note** When printing from a file in the pages folder, `dash_page_registry` may not be complete.  See the "Print page_registry" docs for more info.'
    )

    modules = "ALL" if modules == "__main__" else modules
    if include is None or exclude == "ALL":
        pprint.pprint(dash.page_registry.keys())
        return

    if isinstance(modules, str):
        modules = [modules]
    if isinstance(exclude, str):
        exclude = [exclude]
    if isinstance(include, str):
        include = [include]

    registry = {}
    for page in dash.page_registry.values():
        if modules == ["ALL"] or page["module"] in modules:
            page_items = {}
            for k, v in page.items():
                if include == ["ALL"] or k in include:
                    if exclude is None or k not in exclude:
                        page_items[k] = v
            registry[page["module"]] = page_items
    pprint.pprint(registry, sort_dicts=False)
