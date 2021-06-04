from abc import ABC


class BaseLongCallbackManager(ABC):
    def init(self, app):
        raise NotImplementedError

    def cancel_future(self, key):
        raise NotImplementedError

    def terminate_unhealthy_future(self, key):
        raise NotImplementedError

    def has_future(self, key):
        raise NotImplementedError

    def get_future(self, key, default=None):
        raise NotImplementedError

    def make_background_fn(self, fn, progress=False):
        raise NotImplementedError

    def call_and_register_background_fn(self, key, background_fn, args):
        raise NotImplementedError

    def get_progress(self, key):
        raise NotImplementedError

    def result_ready(self, key):
        raise NotImplementedError

    def get_result(self, key):
        raise NotImplementedError
