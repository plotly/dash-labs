import uuid
from dash.development.base_component import Component


def build_id(id=None, **kwargs):
    if id is not None and id is not Component.UNDEFINED:
        if isinstance(id, dict):
            return id
        else:
            return dict({"id": id}, **kwargs)
    else:
        id = str(uuid.uuid4())
        return dict({"id": id}, **kwargs)


def filter_kwargs(**kwargs):
    return {k: v for k, v in kwargs.items()
            if v is not None and v is not Component.UNDEFINED}
