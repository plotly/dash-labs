import functools
import itertools
import json
import os
import time
import base64
import secrets
import typing
import inspect
import warnings
import collections.abc
from typing import Any

from itsdangerous import Signer, BadSignature

import flask
import appdirs
from _plotly_utils.utils import PlotlyJSONEncoder

from dash import dcc, Output, Input, html, exceptions as dash_errors, page_registry

from dash.development.base_component import Component

_activation_error_message = """
No backend defined for storing session data, choose from DiskSessionBackend, RedisSessionBackend, 
or a custom subclass of `SessionBackend`.
"""


class SessionError(Exception):
    """Error with the session system."""


class SessionInput:
    """
    Used alongside ``session.callback``, trigger a callback when the linked ``key``
    is updated.

    When used with ``sync_session_values``, will be automatically triggered when
    the component value change on the frontend.
    """

    def __init__(self, key: str):
        """
        :param key: Linked session value.
        """
        self.key = key


class SessionState(SessionInput):
    pass


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

    Accessing session items always return a `SessionValue` proxy object, to get the
    actual value for use in format or math operations, you need to call the value
    eg: ``value = session.num_one() + session.num_two()``

    **Example**

    .. code-block::

        import datetime

        from dash import Dash, html, dcc, Output

        from dash_labs.session.backends.diskcache import DiskcacheSessionBackend
        from dash_labs.session import session, setup_sessions, SessionInput, SessionState

        app = Dash(__name__)

        setup_sessions(app, DiskcacheSessionBackend())

        # Set default values in the global scope.
        session.guest_name = 'guest'
        session.posts = []
        session.num_posts = 0

        app.layout = html.Div([
            html.H2('Enter a guest name'),
            # session.guess_name will be synced with the input value.
            dcc.Input(value=session.guest_name),

            html.Div([
                dcc.Input(value=session.current_post, id='new-post'),
                html.Button('New post', n_clicks=session.num_posts),
            ]),

            html.Div(id='session-stats'),
            # Put all the posts in reverse order for last posted first.
            html.Div(session.posts, style={'display': 'flex', 'flexDirection': 'column-reverse'}),
        ])


        @session.callback(
            Output('session-stats', 'children'),
            SessionInput('num_posts'),
            SessionState('posts')
        )
        def on_new_post(_, posts):
            # Can save components as session values
            session.posts = posts + [
                html.Div([
                    # Use the session.current_post current value, reset later
                    html.Div(session.current_post()),
                    html.Div(
                        f'Posted at: {datetime.datetime.now().isoformat()}',
                        style={'fontWeight': 'bold', 'fontStyle': 'italic'}
                    )
                ])
            ]
            # Reset the current post input
            session.current_post = ''
            # To use session values inside f-string or format you
            # need to call to get the actual value.
            return f'Thank you for submitting your {session.num_posts()} post'


        if __name__ == '__main__':
            app.run(debug=True)

    """

    _callbacks = {}

    def __setattr__(self, key, value):
        self.__setitem__(key, value)

    def __getattr__(self, key):
        return self.__getitem__(key)

    def __getitem__(self, key):
        return SessionValue(key)

    def __setitem__(self, key, value) -> None:
        if flask.has_request_context():
            _check_backend()
            flask.g.session_changes[key] = value
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

    def callback(
        self,
        output: typing.Union[Output, typing.List[Output]],
        inputs: typing.Union[SessionInput, typing.List[SessionInput]],
        states: typing.Union[SessionState, typing.List[SessionState]] = None,
    ):
        """
        Add a callback to run when a session value changes.

        :param output: Component properties to update
        :param inputs: Session input keys.
        :param states: Session state to include in the
        """

        def wrap(func):
            inpts = inputs if isinstance(inputs, (list, tuple)) else [inputs]

            for key in inpts:
                Session._callbacks[key.key] = {
                    "func": func,
                    "output": output,
                    "inputs": inpts,
                    "states": [states] if isinstance(states, SessionState) else states,
                    "multi": isinstance(output, (list, tuple)),
                }

            return func

        return wrap


class SessionValue:
    """
    Insert a session value into a layout. Returned by ``session.<key>`` when
    not in a callback.

    When ``sync_session_values`` is True, session values used in a layout
    will automatically create a callback to update the value on the backend
    when the linked component property change.

    Not meant to be used directly, returned by accessing session values when not in
    a request context.
    """

    _watched = collections.defaultdict(list)
    _session_values_indexes = collections.defaultdict(int)
    _started = False

    def __init__(self, key: str):
        self.key = key
        self.component_id = None
        self.component_property = None
        SessionValue._watched[key].append(self)

    def __call__(self):
        if flask.has_request_context():
            _check_backend()
            value = flask.g.session_backend.get(flask.g.session_id, self.key)
            if value is SessionBackend.undefined:
                if self.key in SessionBackend.defaults:
                    # Set missing defaults values for session created before the default
                    # value is added.
                    value = SessionBackend.defaults[self.key]
                    flask.g.session_backend.set(flask.g.session_id, self.key, value)
                else:
                    value = None
            return value
        else:
            raise SessionError("Using session object outside of a request context!")

    def to_plotly_json(self):
        if not self.component_id and not self._started:
            stack = inspect.stack()
            for s in stack:
                if s.function == "iterencode":
                    # The dictionary of props where the session value come from is last - 1
                    # Python >= 3.7 required to guarantee order.
                    markers = list(s.frame.f_locals["markers"].values())
                    props = markers[-2]

                    if not isinstance(props, dict):
                        # Used in array, no sync
                        break
                    component_id = props.get("id")
                    if not component_id:
                        # two up you get the actual component, need to set the id!!!
                        component = markers[-4]
                        if not isinstance(component, Component):
                            # Used in a dictionary, no sync
                            break
                        index = SessionValue._session_values_indexes[self.key]
                        component_id = f"_session-value-bind-{self.key}-{index}"
                        props["id"] = component_id
                        SessionValue._session_values_indexes[self.key] += 1
                        setattr(component, "id", component_id)

                    self.component_id = component_id
                    # Now find the property name
                    for key, value in props.items():
                        if value is self:
                            self.component_property = key
                            break

                if self.component_id:
                    break

        return self()

    def __repr__(self):
        return f"<SessionValue {self.key}>"

    def __eq__(self, other):
        return (
            isinstance(other, SessionValue)
            and other.key == self.key
            and self.component_id == other.component_id
            and self.component_property == other.component_property
        )

    def __hash__(self):
        return hash((self.key, self.component_id, self.component_property))


class SessionBackend:
    """
    Base class to save & load sessions.
    """

    defaults = {}
    undefined = object()

    def set(self, session_id: str, key: str, value: Any):
        """
        Set a key for the session id.

        :param session_id: Session to set data with a key.
        :param key: Key to set
        :param value: Value to store for the session.
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


def _create_sync_key(session_value):
    return f"_dash-session-sync-{session_value.key}-{session_value.component_id}-{session_value.component_property}"


def setup_sessions(
    app,
    backend,
    session_cookie="_dash_sessionid",
    max_age=84600 * 31,
    refresh_after=84600 * 7,
    sync_session_values=True,
    sync_initial_session_values=False,
):
    """
    Set up the session system to add a session cookie to Dash responses.

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
    :param sync_session_values: Session values used in the global layout will be automatically
        synced with the associated component property.
    :type sync_session_values: bool
    :param sync_initial_session_values: Prevent initial callbacks for setting the initial session values
        on the components, can be used if
    """
    key, salt = _session_keys(appdirs.user_config_dir("dash"))

    signer = Signer(key, salt=salt)

    callbacks_setup = {}

    if not isinstance(backend, SessionBackend):
        raise SessionError(f"Invalid session backend: {repr(backend)}")

    @app.server.before_request
    def session_middleware():
        flask.g.session_backend = backend
        flask.g.session_changes = {}

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

        if not sync_session_values or "setup" in callbacks_setup:
            return

        if app.use_pages:
            # Do not assume we went through pages setup
            layout = html.Div(
                [
                    page["layout"]() if callable(page["layout"]) else page["layout"]
                    for page in page_registry.values()
                ]
                + [
                    # pylint: disable=not-callable
                    app.layout()
                    if callable(app.layout)
                    else app.layout
                ]
            )
        else:
            layout = app.layout() if callable(app.layout) else app.layout

        # Dump the layout so all SessionValue's will get their id & prop.
        # We already went through before_first_request, all pages should be enabled.
        json.dumps(layout, cls=PlotlyJSONEncoder)

        # Now the stores can be constructed.
        stores = [
            dcc.Store(id=_create_sync_key(v))
            for v in itertools.chain(*[set(w) for w in SessionValue._watched.values()])
        ]

        app._extra_components.extend(stores)

        if app.use_pages:
            layout.children.extend(stores)
            app.validation_layout = layout

        def set_value(val, session_key=None):
            session[session_key] = val
            # No use in returning the value,
            # but don't return no_update as SessionInput's need a response
            return ""

        for session_value in itertools.chain(
            *[set(v) for v in SessionValue._watched.values()]
        ):
            if not session_value.component_id or not session_value.component_property:
                # Not used in the layout
                continue
            inp = Input(session_value.component_id, session_value.component_property)
            result = Output(_create_sync_key(session_value), "data")

            try:
                app.callback(
                    result,
                    inp,
                    prevent_initial_call=not sync_initial_session_values,
                )(functools.partial(set_value, session_key=session_value.key))
            except dash_errors.DuplicateCallback:
                pass

        callbacks_setup["setup"] = True
        SessionValue._started = True

    @app.server.after_request
    def session_changes(response: flask.Response):
        if "_dash-update-component" in flask.request.path:
            to_change = {}
            changes = list(flask.g.session_changes.items())

            while len(changes):

                # Reset changes for chaining callbacks.
                flask.g.session_changes = {}

                # FIXME prevent circular session callbacks.

                for k, value in changes:
                    if k in Session._callbacks:
                        spec = Session._callbacks[k]
                        result = spec["func"](
                            *[
                                session.get(k.key)()
                                for k in (spec["inputs"] + (spec["states"] or []))
                            ]
                        )

                        if spec["multi"]:
                            for out, res in zip(spec["output"], result):
                                to_change.setdefault(out.component_id, {})
                                to_change[out.component_id][
                                    out.component_property
                                ] = res
                        else:
                            output = spec["output"]
                            to_change.setdefault(output.component_id, {})
                            to_change[output.component_id][
                                output.component_property
                            ] = result

                    # Sync session values that were updated.
                    if k in SessionValue._watched:
                        for session_value in SessionValue._watched[k]:
                            if (
                                not session_value.component_id
                                or not session_value.component_property
                            ):
                                # Not used in the layout
                                continue
                            to_change.setdefault(session_value.component_id, {})
                            to_change[session_value.component_id][
                                session_value.component_property
                            ] = value

                changes = list(flask.g.session_changes.items())

            if to_change:
                try:
                    data = json.loads(response.data)
                    if "response" in data:
                        data["response"].update(to_change)
                    response.set_data(json.dumps(data, cls=PlotlyJSONEncoder))
                except Exception as err:
                    raise SessionError(
                        "Session callbacks can only works from callbacks that returns something, "
                        "Make sure you are not returning `no_update` after setting a session value "
                        "that is linked to a `SessionInput`"
                    ) from err

        return response


session = Session()
