class ComponentPlugin:
    @property
    def inputs(self):
        raise NotImplementedError

    @property
    def output(self):
        raise NotImplementedError

    def build(self, inputs_value):
        raise NotImplementedError
