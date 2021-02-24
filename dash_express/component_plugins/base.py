class ComponentPlugin:
    @property
    def args(self):
        raise NotImplementedError

    @property
    def output(self):
        raise NotImplementedError

    def build(self, inputs_value):
        raise NotImplementedError
