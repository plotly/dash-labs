import json
import os

import pytest

from dash import (
    Dash,
    html,
    dcc,
    Input,
    Output,
    State,
    ctx,
    no_update,
)
from dash.testing.application_runners import ThreadedRunner
from dash.testing.composite import DashComposite

from dash_labs.session import session, setup_sessions, SessionInput, SessionState
from dash_labs.session.backends.diskcache import DiskcacheSessionBackend
from dash_labs.session.backends.redis import RedisSessionBackend
from dash_labs.session.backends.postgres import PostgresSessionBackend


backends = [DiskcacheSessionBackend()]

if "REDIS_URL" in os.environ:
    backends.append(
        RedisSessionBackend(*RedisSessionBackend.split_url(os.environ["REDIS_URL"])),
    )

if "POSTGRESQL_DSN" in os.environ:
    backends.append(
        PostgresSessionBackend(
            **PostgresSessionBackend.split_dsn(os.environ["POSTGRESQL_DSN"])
        )
    )


@pytest.fixture(scope="module", params=backends)
def session_trio(request):
    app = Dash(__name__)
    setup_sessions(app, request.param)

    # Session set in the global scope are defaults for all sessions.
    session.with_default = "Hello Session"

    session.custom_default = lambda _: "custom"

    session.component_default = html.Div("Default component", id="default-component")

    session.number = 10
    session.number_0 = 0
    session.array = [1, 2, 3]
    session.obj = {
        "a": "a",
        "b": 1,
    }
    session.n_clicks = 0
    session.intermediate = 0
    session.in_arr = "arr"
    session.in_dict = "dict"

    app.layout = html.Div(
        [
            # Use session values directly in the layout on serve.
            html.Div(session.with_default, id="with-default"),
            html.Div(session.later_on, id="later_on"),
            html.Div(session.custom_default, id="custom-default"),
            html.Div(session.component_default),
            dcc.Input(id="later-input"),
            dcc.Input(session.synced, id="synced"),
            html.Button("Set later", id="set-later"),
            html.Button("Clear later", id="clear-later"),
            html.Button("set-types", id="set-types"),
            html.Div(id="types-output"),
            html.Div(id="component-output"),
            html.Div(id="dummy"),
            html.Button("set component", id="set-component"),
            html.Button("output component", id="output-component"),
            html.Div(id="session-keys"),
            html.Button("set session keys", id="set-session-keys"),
            html.Button("sync-check", id="sync-check"),
            html.Div(id="sync-output"),
            html.Div(id="session-callback"),
            html.Button("clicks", n_clicks=session.n_clicks, id="n_clicks"),
            html.Div(id="session-multi-sync-state"),
            html.Div(id="session-clicks"),
            html.Div(id="intermediate"),
            html.Div(["arr ", session.in_arr], id="in-arr"),
            dcc.Store(id="store", data={"inside": session.in_dict}),
            html.Div(id="store-output"),
        ]
    )

    @app.callback(
        Output("later_on", "children"),
        [
            Input("set-later", "n_clicks"),
            Input("clear-later", "n_clicks"),
            State("later-input", "value"),
        ],
        prevent_initial_call=True,
    )
    def add_later(*_):
        if ctx.triggered_id == "clear-later":
            value = ""
            del session["later_on"]
        else:
            value = ctx.states["later-input.value"]
            session.later_on = value
        return value

    @app.callback(
        Output("types-output", "children"),
        [Input("set-types", "n_clicks")],
        prevent_initial_call=True,
    )
    def add_types(*_):
        return json.dumps(
            {
                "number": session.number(),
                "number_0": session.number_0(),
                "array": session.array(),
                "obj": session.obj(),
            }
        )

    @app.callback(
        Output("dummy", "children"),
        [Input("set-component", "n_clicks")],
        prevent_initial_call=True,
    )
    def set_component(*_):
        session.callback_component = html.Div(
            "callback component", id="callback-component"
        )
        return no_update

    @app.callback(
        Output("component-output", "children"),
        [Input("output-component", "n_clicks")],
        prevent_initial_call=True,
    )
    def output_component(*_):
        return session.callback_component

    @app.callback(
        Output("session-keys", "children"),
        Input("set-session-keys", "n_clicks"),
    )
    def output_keys(_):
        return json.dumps(list(session))

    @session.callback(
        Output("session-callback", "children"),
        SessionInput("synced"),
    )
    def on_session_value(value):
        return f"From session: {value}"

    @session.callback(
        [
            Output("session-multi-sync-state", "children"),
            Output("session-clicks", "children"),
        ],
        SessionInput("n_clicks"),
        SessionState("synced"),
    )
    def session_multi_callback(clicks, sync):
        session.intermediate = clicks
        return f"State: {sync}", f"Clicks: {clicks}"

    @session.callback(
        Output("intermediate", "children"),
        SessionInput("intermediate"),
    )
    def intermedium(intermediate):
        return f"Intermediate: {intermediate}"

    @app.callback(Output("sync-output", "children"), Input("sync-check", "n_clicks"))
    def sync_check(_):
        return f"Synced: {session.synced()}"

    @app.callback(Output("store-output", "children"), Input("store", "data"))
    def store_output(data):
        return data["inside"]

    runner = ThreadedRunner()
    with DashComposite(
        runner,
        browser=request.config.getoption("webdriver"),
        remote=request.config.getoption("remote"),
        remote_url=request.config.getoption("remote_url"),
        headless=request.config.getoption("headless"),
        options=request.config.hook.pytest_setup_options(),
        download_path=None,
        percy_assets_root=request.config.getoption("percy_assets"),
        percy_finalize=request.config.getoption("nopercyfinalize"),
        pause=request.config.getoption("pause"),
    ) as duo:
        duo.start_server(app)
        yield duo

    try:
        runner.stop()
    except:
        pass


def test_sess001_session_default(session_trio):
    session_trio.wait_for_text_to_equal("#with-default", "Hello Session", timeout=2)


def test_sess002_session_custom_default(session_trio):
    session_trio.wait_for_text_to_equal("#custom-default", "custom", timeout=2)


def test_sess003_session_later(session_trio):
    session_trio.find_element("#later-input").send_keys("later")
    session_trio.find_element("#set-later").click()
    session_trio.wait_for_page()

    session_trio.wait_for_text_to_equal("#later_on", "later")

    session_trio.find_element("#clear-later").click()
    session_trio.wait_for_page()

    assert session_trio.find_element("#later_on").text == ""


def test_sess004_session_types(session_trio):
    session_trio.find_element("#set-types").click()
    session_trio.wait_for_contains_text("#types-output", "{")
    content = session_trio.find_element("#types-output")
    content = json.loads(content.text)

    assert content["number"] == 10
    assert content["number_0"] == 0
    assert content["array"] == [1, 2, 3]
    assert content["obj"]["a"] == "a"
    assert content["obj"]["b"] == 1


def test_sess005_session_components_type_default(session_trio):
    session_trio.wait_for_text_to_equal(
        "#default-component", "Default component", timeout=2
    )


def test_sess006_session_component_type_callback(session_trio):
    session_trio.find_element("#set-component").click()
    session_trio.find_element("#output-component").click()
    session_trio.wait_for_text_to_equal("#callback-component", "callback component")


def test_sess007_session_get_keys(session_trio):
    session_keys = session_trio.find_element("#session-keys")
    session_keys = json.loads(session_keys.text)

    assert "with_default" in session_keys
    assert "custom_default" in session_keys
    assert "component_default" in session_keys


def test_sess008_session_sync(session_trio):
    sync_input = session_trio.find_element("#synced")

    sync_input.send_keys("synced")
    session_trio.wait_for_text_to_equal("#session-callback", "From session: synced")

    session_trio.find_element("#sync-check").click()
    session_trio.wait_for_text_to_equal("#sync-output", "Synced: synced")


def test_sess009_session_callback(session_trio):
    sync_input = session_trio.find_element("#synced")

    session_trio.clear_input(sync_input)

    sync_input.send_keys("callback")

    session_trio.find_element("#n_clicks").click()
    session_trio.wait_for_text_to_equal("#session-multi-sync-state", "State: callback")
    session_trio.wait_for_text_to_equal("#session-clicks", "Clicks: 1")
    session_trio.wait_for_text_to_equal("#intermediate", "Intermediate: 1")


def test_sess010_session_value_in_array(session_trio):
    session_trio.wait_for_text_to_equal("#in-arr", "arr arr")


def test_sess011_session_value_in_dict(session_trio):
    session_trio.wait_for_text_to_equal("#store-output", "dict")
