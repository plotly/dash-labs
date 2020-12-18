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


def build_component_id(kind, link=None, link_source_prop=None, name=None):
    link = link or ""
    link_source_prop = link_source_prop or ""
    name = "" if name is None else name
    return build_id(
        kind=kind,
        link=link,
        link_source_prop=link_source_prop,
        name=name
    )


def filter_kwargs(**kwargs):
    return {k: v for k, v in kwargs.items()
            if v is not None and v is not Component.UNDEFINED}
