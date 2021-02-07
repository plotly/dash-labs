import dash_express as dx


def flat_deps(component, props, kind):
    return dx.arg(component, props=props, kind=kind).flat_dependencies
