import json
from typing import Any

import appdirs

from _plotly_utils.utils import PlotlyJSONEncoder

from dash_labs.session import SessionBackend


_cachedir = appdirs.user_cache_dir("dash-sessions")


class DiskcacheSessionBackend(SessionBackend):
    """
    Diskcache based session backend, store session data using the local filesystem.

    **Example**

    .. code-block::

        from dash import Dash

        from dash_labs.session.backends.diskcache import DiskcacheSessionBackend
        from dash_labs.session import setup_sessions

        app = Dash(__name__)
        setup_sessions(
            app,
            DiskcacheSessionBackend(directory='./session-cache')
        )
    """

    def __init__(self, directory=_cachedir, expire=None, disk=None, **settings):
        """
        :param directory: Directory where the session data will be kept.
        :param expire: Remove session data that has not been used in seconds.
        :param disk: A custom disk to use with the cache. Defaults to a custom JSONDisk to serialize components.
        """
        try:
            import diskcache
            import zlib
        except ImportError as err:
            raise ImportError(
                "Diskcache is not installed, install it with "
                "`pip install dash-labs[diskcache]`"
            ) from err

        # Pickle not safe, users most probably going to store user input.
        class PlotlyJSONDisk(diskcache.Disk):
            def __init__(self, direct, compress_level=1, **kwargs):
                self.compress_level = compress_level
                super().__init__(direct, **kwargs)

            def put(self, key):
                json_bytes = json.dumps(key, cls=PlotlyJSONEncoder).encode("utf-8")
                data = zlib.compress(json_bytes, self.compress_level)
                return super().put(data)

            def get(self, key, raw):
                data = super().get(key, raw)
                if not isinstance(data, str):
                    return json.loads(zlib.decompress(data).decode("utf-8"))
                return data  # Get keys

            def store(self, value, read, key=diskcache.UNKNOWN):
                if not read:
                    json_bytes = json.dumps(value, cls=PlotlyJSONEncoder).encode(
                        "utf-8"
                    )
                    value = zlib.compress(json_bytes, self.compress_level)
                return super().store(value, read, key=key)

            def fetch(self, mode, filename, value, read):
                data = super().fetch(mode, filename, value, read)
                if not read:
                    data = json.loads(zlib.decompress(data).decode("utf-8"))
                return data

        self.cache = diskcache.Cache(
            directory=directory, disk=disk or PlotlyJSONDisk, **settings
        )
        self.lock = diskcache.Lock(self.cache, "session")
        self.expire = expire

    def get(self, session_id: str, key: str):
        return self.cache.get(f"{session_id}/{key}", default=self.undefined)

    def set(self, session_id: str, key: str, value: Any):
        with self.lock:
            self.cache.set(f"{session_id}/{key}", value, expire=self.expire)

    def delete(self, session_id: str, key: str):
        with self.lock:
            self.cache.delete(f"{session_id}/{key}")

    def get_keys(self, session_id: str):
        return (k.split("/")[-1] for k in self.cache.iterkeys() if session_id in k)
