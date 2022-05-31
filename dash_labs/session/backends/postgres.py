import functools
import json
from typing import Any

from _plotly_utils.utils import PlotlyJSONEncoder

from dash_labs.session import SessionBackend


def interpolate_str(template, start_bracket="{%", end_bracket="%}", **data):
    s = template
    for k, v in data.items():
        key = start_bracket + k + end_bracket
        s = s.replace(key, v)
    return s


_sql_formatter = functools.partial(interpolate_str, start_bracket="${", end_bracket="}")

_create_session_table_statement = """
CREATE TABLE  ${schema}.${table} (
    session_id VARCHAR (64) NOT NULL,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW(),
    data JSONB NOT NULL,
    PRIMARY KEY (session_id)
)
"""
_insert_session_statement = """
INSERT INTO ${schema}.${table} (session_id, data) VALUES (%s, %s)
"""

_update_session_statement = """
UPDATE ${schema}.${table}
SET data = jsonb_set(data, %s, %s, true)
WHERE session_id = %s;
"""

_trigger_func_statement = """
CREATE OR REPLACE FUNCTION trigger_set_timestamp()
RETURNS TRIGGER AS $$
BEGIN
  NEW.updated_at = NOW();
  RETURN NEW;
END;
$$ LANGUAGE plpgsql
"""

_trigger_statement = """
CREATE TRIGGER set_timestamp
BEFORE UPDATE ON ${schema}.${table}
FOR EACH ROW
EXECUTE PROCEDURE trigger_set_timestamp();
"""

_table_exists_statement = """
SELECT EXISTS(
    SELECT * FROM information_schema.tables
    WHERE table_schema = %s AND table_name = %s
);
"""

_get_session_value_statement = """
SELECT data -> %s
FROM ${schema}.${table}
WHERE session_id = %s
"""

_delete_session_value_statement = """
UPDATE ${schema}.${table}
SET data = data - %s
WHERE session_id = %s;
"""

_get_keys_statement = """
SELECT jsonb_object_keys(data)
FROM ${schema}.${table}
WHERE session_id = %s;
"""


def _table_exists(cursor, schema, table):
    cursor.execute(_table_exists_statement, [schema, table])
    result = cursor.fetchone()
    if result:
        return result[0]


class PostgresSessionBackend(SessionBackend):
    """
    PostgresSQL session backend stores the data in `session` table.
    """

    def __init__(
        self,
        user=None,
        password=None,
        host="localhost",
        port="5432",
        database="postgres",
        schema="public",
        table="session",
        min_conn=1,
        max_conn=50,
        create_table=True,
        **settings
    ):

        try:
            import psycopg2
            from psycopg2 import pool
            from psycopg2.extras import Json
        except ImportError as err:
            raise ImportError(
                "Install dash[postgresql] to use this session backend."
            ) from err

        self.pool = psycopg2.pool.ThreadedConnectionPool(
            min_conn,
            max_conn,
            user=user,
            password=password,
            host=host,
            port=port,
            database=database,
            **settings,
        )
        self.schema = schema
        self.table = table
        self._json = functools.partial(
            Json, dumps=functools.partial(json.dumps, cls=PlotlyJSONEncoder)
        )
        self._insert_statement = _sql_formatter(
            _insert_session_statement,
            schema=schema,
            table=table,
        )
        self._update_statement = _sql_formatter(
            _update_session_statement,
            schema=schema,
            table=table,
        )
        self._get_statement = _sql_formatter(
            _get_session_value_statement,
            schema=schema,
            table=table,
        )
        self._delete_statement = _sql_formatter(
            _delete_session_value_statement,
            schema=schema,
            table=table,
        )
        self._get_keys_statement = _sql_formatter(
            _get_keys_statement,
            schema=schema,
            table=table,
        )
        if create_table:
            self._setup_table()

    def _setup_table(self):
        conn = self.pool.getconn()
        try:
            with conn.cursor() as cursor:
                exists = _table_exists(cursor, self.schema, self.table)
                if not exists:
                    cursor.execute(
                        _sql_formatter(
                            _create_session_table_statement,
                            schema=self.schema,
                            table=self.table,
                        ),
                    )
                    cursor.execute(_trigger_func_statement)
                    cursor.execute(
                        _sql_formatter(
                            _trigger_statement,
                            schema=self.schema,
                            table=self.table,
                        ),
                    )
                conn.commit()
        finally:
            self.pool.putconn(conn)

    def set(self, session_id: str, key: str, value: Any):
        conn = self.pool.getconn()
        try:
            with conn.cursor() as cursor:
                cursor.execute(
                    self._update_statement, [[key], self._json(value), session_id]
                )
            conn.commit()
        finally:
            self.pool.putconn(conn)

    def get(self, session_id: str, key: str):
        conn = self.pool.getconn()
        try:
            with conn.cursor() as cursor:
                cursor.execute(self._get_statement, [key, session_id])
                value = cursor.fetchone()
                if value:
                    return value[0]
                return self.undefined
        finally:
            self.pool.putconn(conn)

    def delete(self, session_id: str, key: str):
        conn = self.pool.getconn()
        try:
            with conn.cursor() as cursor:
                cursor.execute(self._delete_statement, [key, session_id])
            conn.commit()
        finally:
            self.pool.putconn(conn)

    def on_new_session(self, session_id: str):
        conn = self.pool.getconn()
        try:
            with conn.cursor() as cursor:
                cursor.execute(
                    self._insert_statement,
                    [
                        session_id,
                        self._json(
                            {
                                k: v(session_id) if callable(v) else v
                                for k, v in SessionBackend.defaults.items()
                            }
                        ),
                    ],
                )
            conn.commit()
        finally:
            self.pool.putconn(conn)

    def get_keys(self, session_id: str):
        conn = self.pool.getconn()
        try:
            with conn.cursor() as cursor:
                cursor.execute(self._get_keys_statement, [session_id])
                for row in cursor:
                    yield row[0]
        finally:
            self.pool.putconn(conn)

    @staticmethod
    def split_dsn(dsn):
        s = dsn.split(" ")
        data = {}
        for key, value in (d.split("=") for d in s):
            data[key] = value
        return data
