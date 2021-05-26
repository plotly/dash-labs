from abc import ABC

class LongCallbackBackend(ABC):

    def send_result(self, value):
        pass

    def send_progress(self, progress, total):
        pass


