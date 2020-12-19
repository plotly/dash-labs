import uuid
from dash.development.base_component import Component
from dash.dependencies import ALL


def build_id(id=None, **kwargs):
    if id is not None and id is not Component.UNDEFINED:
        if isinstance(id, dict):
            return id
        else:
            return dict({"id": id}, **kwargs)
    else:
        id = str(uuid.uuid4())
        return dict({"id": id}, **kwargs)


def build_component_id(kind, name=None):
    if name is None:
        name = kind
    return build_id(
        kind=kind,
        name=name
    )


def is_component_id(id):
    return isinstance(id, dict) and "name" in id and "kind" in id


def build_component_pattern(
        id=ALL, kind=ALL,
        label_link=ALL,  label_link_prop=ALL,
        disable_link=ALL, disable_link_prop=ALL,
        name=ALL,
        **kwargs
):
    return dict(
        id=id, kind=kind,
        label_link=label_link, label_link_prop=label_link_prop,
        disable_link=disable_link, disable_link_prop=disable_link_prop,
        name=name,
        **kwargs
    )



def filter_kwargs(**kwargs):
    return {k: v for k, v in kwargs.items()
            if v is not None and v is not Component.UNDEFINED}
