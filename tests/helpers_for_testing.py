import dash_express as dx


def flat_deps(component, props, kind):
    dep = {"input": dx.Input, "state": dx.State, "output": dx.Output}[kind]
    return dep(component, props).flat_dependencies
