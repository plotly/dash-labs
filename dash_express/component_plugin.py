class ParameterPlugin:
    @property
    def inputs(self):
        raise NotImplementedError

    @property
    def output(self):
        raise NotImplementedError

    @property
    def build(self, inputs_value, **kwargs):
        raise NotImplementedError
