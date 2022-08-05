import json
from typing import Any

from _plotly_utils.utils import PlotlyJSONEncoder

from dash_labs.session import SessionBackend


class RedisSessionBackend(SessionBackend):
    """
    Session backend using redis.

    **Setup example:**

    .. code-block::

        from dash import Dash

        from dash_labs.session.backends.redis import RedisSessionBackend
        from dash_labs.session import setup_sessions

        app = Dash(__name__)
        setup_sessions(
            app,
            RedisSessionBackend(host='localhost', port=6379, db=0)
        )
    """

    def __init__(
        self, host="localhost", port=6379, db=0, expire: int = None, **connection_kwargs
    ):
        try:
            import redis
        except ImportError as err:
            raise ImportError(
                "Diskcache is not installed, install it with "
                "`pip install dash-labs[redis]`"
            ) from err

        self.pool = redis.ConnectionPool(
            host=host, port=port, db=db, **connection_kwargs
        )
        self.r = redis.Redis(connection_pool=self.pool)
        self.expire = expire

    @staticmethod
    def _session_key(session_id):
        return f"dash/session/{session_id}"

    def get(self, session_id: str, key: str):
        # redis don't keep types so values are serialized to json.
        value = self.r.hget(self._session_key(session_id), key)
        if value:
            return json.loads(value)
        else:
            return self.undefined

    def set(self, session_id: str, key: str, value: Any):
        self.r.hset(
            self._session_key(session_id), key, json.dumps(value, cls=PlotlyJSONEncoder)
        )
        if self.expire:
            self.r.expire(self._session_key(session_id), self.expire)

    def delete(self, session_id: str, key: str):
        self.r.hdel(self._session_key(session_id), key)

    def get_keys(self, session_id: str):
        keys = self.r.hkeys(self._session_key(session_id))
        return (k.decode() for k in keys)

    @staticmethod
    def split_url(url):
        host, rest = url.split("://")[-1].split(":")
        if "/" in rest:
            port, db = rest.split("/", 1)
        else:
            port = rest
            db = 0
        return host, port, db
