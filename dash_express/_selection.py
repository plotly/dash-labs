def select(component, name=None, kind=None):
    from dash.development.base_component import Component

    if not isinstance(component, Component):
        raise ValueError(
            "select requires a Dash component\n"
            f"    Received object of type {type(component)}: {component}"
        )

    def matches(c):
        if name is None and kind is None:
            return True

        id = getattr(c, "id", None)
        if not isinstance(id, dict):
            return False

        if name is not None and id.get("name", None) != name:
            return False

        if kind is not None and id.get("kind", None) != kind:
            return False

        return True

    if matches(component):
        return [component]
    else:
        children = getattr(component, "children", None)
        if isinstance(children, Component):
            return select(children, name=name, kind=kind)
        elif isinstance(children, list):
            return [
                match
                for child in children if isinstance(child, Component)
                for match in select(child, name=name, kind=kind)
            ]
    return []


def select_one(component, name=None, kind=None):
    selection = select(component, name=name, kind=kind)
    if len(selection) != 1:
        raise ValueError(
            "Selection resulted in {n} matches, but select_first requires there to be exactly 1 match"
        )
    else:
        return selection[0]
