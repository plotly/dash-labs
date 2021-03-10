import dash_labs as dl


def flat_deps(component, props, kind):
    dep = {"input": dl.Input, "state": dl.State, "output": dl.Output}[kind]
    return dep(component, props).flat_dependencies()
