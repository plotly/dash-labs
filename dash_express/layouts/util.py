import uuid
from dash.development.base_component import Component


def build_id(id=None, prefix=None):
    if id is not None and id is not Component.UNDEFINED:
        return id
    else:
        id = str(uuid.uuid4())
        if prefix:
            id = (prefix + "-") + id
        return id


def filter_kwargs(**kwargs):
    return {k: v for k, v in kwargs.items()
            if v is not None and v is not Component.UNDEFINED}
