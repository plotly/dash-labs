import uuid
from dash.development.base_component import Component


def build_id(name, **kwargs):
    uid = str(uuid.uuid4())
    return dict(
        uid=uid,
        name=name,
        **kwargs,
    )


def filter_kwargs(**kwargs):
    return {k: v for k, v in kwargs.items()
            if v is not None and v is not Component.UNDEFINED}
