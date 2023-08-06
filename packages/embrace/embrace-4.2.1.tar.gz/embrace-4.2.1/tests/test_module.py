from contextlib import contextmanager
from tempfile import TemporaryDirectory
from typing import Dict
from unittest.mock import Mock
from unittest.mock import call
import pathlib

import pytest

from embrace import module
from embrace import Module
from embrace.query import known_styles
from embrace.query import Query


@contextmanager
def fs_hierarchy(items: Dict = {}, base=None):

    if base is None:
        with TemporaryDirectory() as tmp:
            with fs_hierarchy(items, pathlib.Path(tmp)) as base:
                yield base
        return

    for filename, contents in items.items():
        if isinstance(contents, Dict):
            (base / filename).mkdir()
            fs_hierarchy(contents, base / filename)
        else:
            with open(base / filename, "w", encoding="utf-8") as f:
                f.write(contents)
    yield base


known_styles[Mock] = "qmark"


def test_it_loads_unnamed():

    with fs_hierarchy({"q1.sql": "SELECT 1"}) as d:
        m = module(d)
        assert isinstance(m.q1, Query)


def test_it_loads_directory():

    with fs_hierarchy(
        {"q1.sql": "-- :name q1\nSELECT 1", "q2.sql": "-- :name q2\nSELECT 2"}
    ) as d:
        m = module(d)
        assert isinstance(m.q1, Query)
        assert isinstance(m.q2, Query)
        assert getattr(m, "q3", None) is None


def test_auto_reloading():
    def write_query_file(name):
        def write_query_file(d):
            with open(d / f"{name}.sql", "w") as f:
                f.write(f"-- :name {name}\nSELECT 1")

        return write_query_file

    def unlink_query_file(name):
        def unlink_query_file(d):
            (d / f"{name}.sql").unlink()

        return unlink_query_file

    def test_reload(files, mod, expected, auto_reload=True):
        with fs_hierarchy(files) as d:
            m = module(d, auto_reload=auto_reload)
            previous = m.queries.copy()
            mod(d)
            for name, what in expected.items():
                actual = getattr(m, name, None)
                if what == "deleted":
                    assert actual is None
                elif what == "unchanged":
                    assert isinstance(actual, Query)
                    assert actual is previous[name]
                elif what == "created":
                    assert isinstance(actual, Query)
                    assert name not in previous
                elif what == "changed":
                    assert isinstance(actual, Query)
                    assert actual is not previous[name]

    def test_no_reload(files, mod, expected):
        return test_reload(files, mod, expected, False)

    q = {"q.sql": "-- :name q\nSELECT 1"}
    test_reload({}, write_query_file("q1"), {"q1": "created"})
    test_reload(q, write_query_file("q"), {"q": "changed"})
    test_reload(q, unlink_query_file("q"), {"q": "deleted"})

    test_no_reload({}, write_query_file("q"), {"q": "deleted"})
    test_no_reload(q, write_query_file("q"), {"q": "unchanged"})
    test_no_reload(q, unlink_query_file("q"), {"q": "unchanged"})


def test_auto_reloading_with_non_file_queries():
    m = module(auto_reload=True)
    q = Query(name="q", source="<string>", statements=["select 1"])
    m.add_query("q", q)
    m.ensure_up_to_date("q")
    assert m.q.__wrapped__ is q


def test_reloadable_query():
    with fs_hierarchy({"q1.sql": "SELECT 1"}) as d:
        conn = Mock()
        known_styles[conn.__class__] = "qmark"
        m = module(d, auto_reload=True)
        query = m.q1

        query(conn)
        assert conn.cursor().execute.call_args == call("SELECT 1", tuple())

        with pathlib.Path(d / "q1.sql").open("w") as f:
            f.write("SELECT 2")

        query(conn)
        assert conn.cursor().execute.call_args == call("SELECT 2", tuple())


def test_binding():

    with fs_hierarchy({"q1.sql": "-- :name q1 :first\nSELECT 1"}) as d:
        conn = Mock()
        known_styles[conn.__class__] = "qmark"
        with module(d).bind(conn) as m:
            m.q1()
            assert conn.cursor().fetchone.called is True


def test_transaction():
    with fs_hierarchy({"q1.sql": "-- :name q1 :first\nSELECT 1"}) as d:
        conn = Mock()
        known_styles[conn.__class__] = "qmark"
        with module(d).transaction(conn) as m:
            m.q1()
            assert conn.cursor().fetchone.called is True
        assert conn.commit.called is True


def test_savepoint():
    with fs_hierarchy({"q1.sql": "-- :name q1 :first\nSELECT 1"}) as d:
        conn = Mock()
        cursor = conn.cursor()
        known_styles[conn.__class__] = "qmark"
        with module(d).savepoint(conn) as m:
            assert cursor.execute.call_args[0][0].startswith("SAVEPOINT sp_")
            m.q1()
            assert cursor.execute.call_args == call("SELECT 1", ())
            assert cursor.fetchone.called is True
        assert cursor.execute.call_args[0][0].startswith("RELEASE SAVEPOINT sp_")


def test_savepoint_rollback():
    class AnException(Exception):
        pass

    with fs_hierarchy({"q1.sql": "-- :name q1 :first\nSELECT 1"}) as d:
        conn = Mock()
        known_styles[conn.__class__] = "qmark"
        cursor = conn.cursor()
        try:
            with module(d).savepoint(conn) as m:
                assert cursor.execute.call_args[0][0].startswith("SAVEPOINT sp_")
                m.q1()
                raise AnException()
        except AnException:
            assert cursor.execute.call_args[0][0].startswith(
                "ROLLBACK TO SAVEPOINT sp_"
            )


def test_returning():
    from test_query import mock_conn

    conn = mock_conn([(1,)], description=[("a",)])
    m = Mock()
    result = Module().query("").returning(m).one(conn)
    assert m.call_args_list == [call(a=1)]
    assert result is m()


def test_it_resolves_includes():
    with fs_hierarchy({"q1.sql": ":include:q2", "q2.sql": "SELECT 1;"}) as d:
        m = module(d)
        assert m.q1.statements == ["SELECT 1"]


def test_it_has_a_useful_repr():

    with fs_hierarchy({"q1.sql": "SELECT 1;"}) as d:
        assert repr(module(d)) == f"<embrace.module.Module {d}>"


def test_it_suggests_matching_query_on_attributeerror():
    with fs_hierarchy({"foobar.sql": "SELECT 1;"}) as d:
        with pytest.raises(AttributeError) as e:
            module(d).foobaz
        assert "Did you mean 'foobar'?" in str(e.value.args[0])
