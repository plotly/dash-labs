import json
import os
import time
import base64
import secrets
import warnings
import collections.abc
from typing import Any

from itsdangerous import Signer, BadSignature

import flask
import appdirs
from _plotly_utils.utils import PlotlyJSONEncoder

_activation_error_message = """
No backend defined for storing session data, choose from DiskSessionBackend, RedisSessionBackend, 
or a custom subclass of `SessionBackend`.
"""


class SessionError(Exception):
    """Error with the session system."""


def _session_keys(directory):
    key = os.getenv("DASH_SESSION_KEY")
    salt = os.getenv("DASH_SESSION_SALT")

    if not key or not salt:
        keyfile = os.path.join(directory, "keys.json")

        if os.path.exists(keyfile):
            with open(keyfile) as f:
                data = json.load(f)

            return data["key"], data["salt"]

        warnings.warn(
            "Keys for session system are generated randomly and stored locally!"
        )

        key = secrets.token_hex(128)
        salt = secrets.token_hex(128)

        os.makedirs(directory, exist_ok=True)
        with open(keyfile, "w") as f:
            json.dump({"key": key, "salt": salt}, f)

    return key, salt


def _check_backend():
    if not hasattr(flask.g, "session_backend"):
        raise SessionError(_activation_error_message)


class Session(collections.abc.MutableMapping):
    """
    Session store data scoped to the current user, use it directly in layout or callbacks.
    """

    def __setattr__(self, key, value):
        self.__setitem__(key, value)

    def __getattr__(self, key):
        return self.__getitem__(key)

    def __getitem__(self, key):
        if flask.has_request_context():
            _check_backend()
            return flask.g.session_backend.get(flask.g.session_id, key)
        return SessionValue(key)

    def __setitem__(self, key, value) -> None:
        if flask.has_request_context():
            _check_backend()
            flask.g.session_backend.set(flask.g.session_id, key, value)
        else:
            # When set in global scope, set as default.
            SessionBackend.defaults[key] = value

    def __delitem__(self, key) -> None:
        _check_backend()
        flask.g.session_backend.delete(flask.g.session_id, key)

    def __len__(self) -> int:
        return len(flask.g.session_backend.get_keys(flask.g.session_id))

    def __iter__(self):
        return flask.g.session_backend.get_keys(flask.g.session_id)

    def __repr__(self):
        if flask.has_request_context():
            data = dict(self)
            return f'<Session\n id="{flask.g.session_id}"\n values={json.dumps(data, indent=2, cls=PlotlyJSONEncoder)}>'
        return "<Session>"


class SessionValue:
    """
    Insert a session value into a layout.
    """

    def __init__(self, key: str):
        self.key = key

    def to_plotly_json(self):
        return session.get(self.key)

    def __repr__(self):
        return f"<SessionValue {self.key}>"


class SessionBackend:
    """
    Base class to save & load sessions.
    """

    defaults = {}

    def set(self, session_id: str, key: str, value: Any):
        """
        Set a key for the session id.

        :param session_id: Session to set data with a key.
        :param key: Key to set
        :param value: Value to keep.
        :return:
        """
        raise NotImplementedError

    def get(self, session_id: str, key: str):
        """
        Get a key for the session id.

        :param session_id: Session to fetch the data for.
        :param key: Key to get.
        :return:
        """
        raise NotImplementedError

    def delete(self, session_id: str, key: str):
        """
        Delete a session key value.

        :param session_id: Session to delete the key for.
        :param key: The key to delete.
        :return:
        """
        raise NotImplementedError

    def on_new_session(self, session_id: str):
        """Called when a new session is created. Set the default session values."""
        for key, value in SessionBackend.defaults.items():
            val = value
            if callable(value):
                val = value(session_id)
            self.set(session_id, key, val)

    def get_keys(self, session_id: str):
        raise NotImplementedError


def setup_sessions(
    app,
    backend,
    session_cookie="_dash_sessionid",
    max_age=84600 * 31,
    refresh_after=84600 * 7,
):
    """
    Setup the session system to add a session cookie to Dash responses.

    :type app: dash.Dash
    :param app: Dash app to add session handlers.
    :type backend: SessionBackend
    :param backend: The backend to store the data with.
    :type session_cookie: str
    :param session_cookie: Name of the session cookie.
    :type max_age: int
    :param max_age: Remove the session cookie from the browser after this amount of seconds.
    :type refresh_after: int
    :param refresh_after: Refresh the session when a request is made after this delay in seconds.
    """
    key, salt = _session_keys(appdirs.user_config_dir("dash"))

    signer = Signer(key, salt=salt)

    if not isinstance(backend, SessionBackend):
        raise SessionError(f"Invalid session backend: {repr(backend)}")

    @app.server.before_request
    def session_middleware():
        flask.g.session_backend = backend

        token = flask.request.cookies.get(session_cookie)

        def set_session(_id):
            ts = base64.b64encode(str(int(time.time())).encode()).decode()

            @flask.after_this_request
            def _set_session(response):
                response.set_cookie(
                    session_cookie,
                    signer.sign(f"{_id}#{ts}").decode(),
                    httponly=True,
                    max_age=max_age,
                    samesite="Strict",
                )
                return response

        def new_session():
            sess_id = secrets.token_hex(32)
            backend.on_new_session(sess_id)
            set_session(sess_id)
            return sess_id

        if not token:
            session_id = new_session()
        else:
            try:
                unsigned = signer.unsign(token).decode()
                session_id, created = unsigned.split("#")

                delta = time.time() - int(base64.b64decode(created))
                if delta > refresh_after:
                    set_session(session_id)
            except BadSignature:
                session_id = new_session()

        flask.g.session_id = session_id


session = Session()
