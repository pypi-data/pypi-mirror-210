from typing import Any
from typing import List
from itertools import islice
from unittest.mock import Mock
from unittest.mock import call
import string

from embrace.query import Query
from embrace.query import ResultSet
from embrace.query import mapobject
from embrace.query import one_to_one
from embrace.query import one_to_many
from embrace.query import known_styles
from embrace.query import get_split_points
from embrace.query import group_by_and_join
from embrace.query import make_rowspec
from embrace import exceptions

import pytest


def mock_conn(rows=None, description=[]):
    conn = Mock()
    known_styles[conn.__class__] = "qmark"

    if rows is not None:

        def fetchone():
            return next(rowiter, None)

        def fetchmany(size=None):
            if size is None:
                size = conn.cursor().arraysize
            return list(islice(rowiter, size))

        rowiter = iter(rows)
        conn.cursor().arraysize = 5
        conn.cursor().fetchone = Mock(side_effect=fetchone)
        conn.cursor().fetchmany = Mock(side_effect=fetchmany)
        conn.cursor().fetchall = Mock(side_effect=lambda: list(rowiter))
    conn.cursor().description = description
    return conn


class MockModel:
    def __init__(self, *args, **kw):
        self.__dict__.update(zip(string.ascii_lowercase, args))
        self.__dict__.update(kw)

    def __eq__(self, other):
        return other.__class__ == self.__class__ and other.__dict__ == self.__dict__

    def __getattr__(self, attr):
        if attr.endswith("s"):
            r: List[Any] = []
            setattr(self, attr, r)
            return r
        raise AttributeError(attr)

    def __repr__(self):
        return f"<{self.__class__.__name__} {self.__dict__!r}>"


def query(rt, statement=""):
    return Query(name="", result_type=rt, statements=[statement], source="")


def test_return_types():
    def test(result_type, rows, expected):
        conn = mock_conn(rows=rows)
        q = query(result_type)
        try:
            result = q(conn)
        except Exception as e:
            assert isinstance(e, expected)
        else:
            if isinstance(expected, list):
                assert list(result) == expected
            elif callable(expected):
                assert result == expected(conn)
            else:
                assert result == expected

    test("one", [], exceptions.NoResultFound)
    test("one", [(1,)], (1,))
    test("one", [(1, 2), (3, 4)], exceptions.MultipleResultsFound)
    test("many", [], [])
    test("many", [(1, 2)], [(1, 2)])
    test("many", [(1, 2), (3, 4)], [(1, 2), (3, 4)])
    test("first", [], None)
    test("first", [(1,)], (1,))
    test("first", [(1, 2, 3), (4, 5, 6)], (1, 2, 3))
    test("one_or_none", [], None)
    test("one_or_none", [(1,)], (1,))
    test("one_or_none", [(1, 2), (3, 4)], exceptions.MultipleResultsFound)
    test("scalar", [], exceptions.NoResultFound)
    test("scalar", [(1,)], 1)
    test("scalar", [(1, 2, 3), (4, 5, 6)], 1)
    test("column", [(1, 2), (3, 4)], [1, 3])
    test("cursor", [], lambda conn: conn.cursor())
    test("affected", [], lambda conn: conn.cursor().rowcount)


def test_mapped_objects_with_no_rows_returned():

    conn = mock_conn(rows=[])
    assert query("one_or_none").returning(dict)(conn) is None
    assert query("first").returning(dict)(conn) is None


def test_can_override_return_type():
    def test(result_type, rows, expected):
        conn = mock_conn(rows=rows)
        q = query("one")
        try:
            result = getattr(q, result_type)(conn)
        except Exception as e:
            assert isinstance(e, expected)
        else:
            if isinstance(expected, list):
                assert list(result) == expected
            elif callable(expected):
                assert result == expected(conn)
            else:
                assert result == expected

    test("one", [], exceptions.NoResultFound)
    test("one", [(1,)], (1,))
    test("one", [(1, 2), (3, 4)], exceptions.MultipleResultsFound)
    test("many", [], [])
    test("many", [(1, 2)], [(1, 2)])
    test("many", [(1, 2), (3, 4)], [(1, 2), (3, 4)])
    test("first", [], None)
    test("first", [(1,)], (1,))
    test("first", [(1, 2, 3), (4, 5, 6)], (1, 2, 3))
    test("one_or_none", [], None)
    test("one_or_none", [(1,)], (1,))
    test("one_or_none", [(1, 2), (3, 4)], exceptions.MultipleResultsFound)
    test("scalar", [], exceptions.NoResultFound)
    test("scalar", [(1,)], 1)
    test("scalar", [(1, 2, 3), (4, 5, 6)], 1)
    test("column", [(1, 2), (3, 4)], [1, 3])
    test("cursor", [], lambda conn: conn.cursor())
    test("affected", [], lambda conn: conn.cursor().rowcount)


def test_it_accepts_params_as_dict():
    q = query("one", "select :x")
    conn = mock_conn(rows=[(1,)])
    q(conn, {"x": 1})
    assert conn.cursor().execute.call_args_list == [call("select ?", (1,))]


def test_it_accepts_params_as_kwargs():
    q = query("one", "select :x")
    conn = mock_conn(rows=[(1,)])
    q(conn, x=1)
    assert conn.cursor().execute.call_args_list == [call("select ?", (1,))]


def test_it_accepts_params_as_both_dict_and_kwargs():
    q = query("one", "select :x, :y")
    conn = mock_conn(rows=[(1,)])
    q(conn, {"x": 1}, y=2)
    assert conn.cursor().execute.call_args_list == [call("select ?, ?", (1, 2))]


def test_queries_return_a_resultset():
    q = query("one")
    conn = mock_conn(rows=[(1,)])
    assert isinstance(q.resultset(conn), ResultSet)
    assert isinstance(q.execute(conn), ResultSet)


class TestResultSet:
    def test_many_uses_fetchmany(self):
        conn = mock_conn(rows=[(1,)] * 100)
        rs = query("x").resultset(conn)
        conn.cursor().arraysize = 5
        assert len(list(rs.many("fetchmany"))) == 100
        assert conn.cursor().fetchmany.call_count == 21

    def test_many_uses_fetchone(self):
        conn = mock_conn(rows=[(1,)] * 100)
        rs = query("x").resultset(conn)
        assert len(list(rs.many("fetchone"))) == 100
        assert conn.cursor().fetchone.call_count == 101

    def test_many_uses_fetchall(self):
        conn = mock_conn(rows=[(1,)] * 100)
        rs = query("x").resultset(conn)
        assert len(list(rs.many("fetchall"))) == 100
        assert conn.cursor().fetchall.call_count == 1

    def test_many_with_limit_uses_fetchmany(self):
        conn = mock_conn(rows=[(1,)] * 100)
        rs = query("x").resultset(conn)
        assert len(list(rs.many("fetchmany", limit_rows=19))) == 19
        assert conn.cursor().fetchmany.call_count == 4

    def test_many_with_limit_uses_fetchone(self):
        conn = mock_conn(rows=[(1,)] * 100)
        rs = query("x").resultset(conn)
        assert len(list(rs.many("fetchone", limit_rows=19))) == 19
        assert conn.cursor().fetchone.call_count == 19

    def test_many_with_limit_uses_fetchall(self):
        q = query("x")
        conn = mock_conn(rows=[(1,)] * 100)
        rs = q.resultset(conn)
        assert len(list(rs.many("fetchall", limit_rows=19))) == 19
        assert conn.cursor().fetchall.call_count == 1

    def test_many_with_limit_mapped(self):
        rows = [(1, 2), (1, 3), (2, 1), (2, 2), (3, 1), (4, 1)]
        expected_mapped = [
            MockModel(id=1, x=[MockModel(id=2), MockModel(id=3)]),
            MockModel(id=2, x=[MockModel(id=1), MockModel(id=2)]),
            MockModel(id=3, x=[MockModel(id=1)]),
            MockModel(id=4, x=[MockModel(id=1)]),
        ]

        for method in ("fetchall", "fetchmany", "fetchone", "auto"):
            for limit in [1, 2, 3, 4, 5, 100]:
                conn = mock_conn(rows=rows, description=[("id",), ("id",)],)
                rs = (
                    query("x")
                    .returning((MockModel, MockModel), joins=(one_to_many(0, "x", 1)))
                    .resultset(conn)
                )

                assert (
                    list(rs.many(method, limit_mapped=limit)) == expected_mapped[:limit]
                )


def test_scalar_returns_default():
    q = query("one")
    assert q.scalar(mock_conn(rows=[]), default="foo") == "foo"
    assert q.scalar(mock_conn(rows=[(1,)]), default="foo") == 1
    with pytest.raises(exceptions.NoResultFound):
        q.scalar(mock_conn(rows=[]))


class TestReturning:
    def test_simple_type_with_keyword_arguments(self):
        conn = mock_conn([(1, 2), (2, 3)], description=[("a",), ("b",)])
        result = list(query("").returning(MockModel).many(conn))
        assert result == [MockModel(a=1, b=2), MockModel(a=2, b=3)]

    def test_simple_type_with_positional_arguments(self):
        conn = mock_conn([(1, 2), (2, 3)], description=[("a",), ("b",)])
        m = Mock()
        result = list(query("").returning(m, positional=True).many(conn))
        assert m.call_args_list == [call(1, 2), call(2, 3)]
        assert result == [m(), m()]

    def test_multi_with_keyword_arguments(self):
        conn = mock_conn([(1, 2, 3, 4)], description=[("id",), ("a",), ("id",), ("b",)])
        a = Mock()
        b = Mock()
        result = query("").returning((a, b), positional=False).one(conn)
        assert a.call_args_list == [call(id=1, a=2)]
        assert b.call_args_list == [call(id=3, b=4)]
        assert result == (a(), b())

    def test_multi_with_positional_arguments(self):
        conn = mock_conn([(1, 2, 3, 4)], description=[("id",), ("a",), ("id",), ("b",)])
        a = Mock()
        b = Mock()
        result = query("").returning((a, b), positional=True).one(conn)
        assert a.call_args_list == [call(1, 2)]
        assert b.call_args_list == [call(3, 4)]
        assert result == (a(), b())

    def test_it_preserves_identity(self):
        conn = mock_conn(rows=[(1, 5), (2, 6), (1, 6)], description=[("a",), ("b",)],)
        result = list(query("").returning((MockModel), key_columns=[("a",)]).many(conn))
        assert result[0] is result[2]
        assert result[0] is not result[1]

        conn = mock_conn(rows=[(1, 5), (1, 6), (2, 6)], description=[("a",), ("b",)],)
        result = list(query("").returning((MockModel), key_columns=[("b",)]).many(conn))
        assert result[0] is not result[1]
        assert result[1] is result[2]

    def test_it_doesnt_preserve_identity(self):
        conn = mock_conn(rows=[(1, 5), (1, 6), (2, 6)], description=[("a",), ("b",)],)
        result = list(query("").returning((MockModel)).many(conn))
        assert result[0] is not result[1]
        assert result[1] is not result[2]

    def test_it_preserves_identity_on_consecutive_objects_without_key_columns(self,):
        conn = mock_conn(rows=[(1, 5), (1, 6), (1, 6)], description=[("id",), ("id",)],)
        result = list(query("").returning((MockModel, MockModel)).many(conn))
        assert result[0][0] is result[1][0]
        assert result[0][0] is result[2][0]
        assert result[0][1] is not result[1][1]
        assert result[0][1] is not result[2][1]
        assert result[1][1] is result[2][1]

    def test_key_columns_has_a_helpful_error(self):

        conn = mock_conn(rows=[], description=[("a",), ("b",)],)
        with pytest.raises(ValueError) as excinfo:
            query("").returning((MockModel), key_columns="c").many(conn)
        assert "'c' specified in key_columns does not exist" in str(excinfo.value)

    def test_object_identity_works_with_unhashable_objects(self):
        conn = mock_conn(rows=[([1], 1), ([1], 1)], description=[("id",), ("id",)],)
        result = list(
            query("")
            .returning((MockModel, MockModel), joins=(one_to_one(0, "x", 1),))
            .many(conn)
        )
        assert result[0] is result[1]

    def test_unfazed_by_empty_resultset(self):
        conn = mock_conn(rows=[], description=[("id",)],)
        result = list(query("").returning((MockModel)).many(conn))
        assert result == []

        conn = mock_conn(rows=[], description=[("id",), ("id",)],)
        result = list(query("").returning((MockModel, MockModel)).many(conn))
        assert result == []

        conn = mock_conn(rows=[], description=[("id",), ("id",)],)
        result = list(
            query("")
            .returning((MockModel, MockModel), joins=[one_to_many(0, "a", 1)])
            .many(conn)
        )
        assert result == []

        conn = mock_conn(rows=[], description=[("id",), ("id",), ("id",)],)
        result = list(
            query("")
            .returning(
                (MockModel, MockModel, MockModel), joins=[one_to_many(1, "a", 2)],
            )
            .many(conn)
        )
        assert result == []

    def test_passthrough(self):
        conn = mock_conn(rows=[(1,), ("fish",)], description=[("id",), ("id",)],)
        result = list(query("").returning(mapobject.passthrough()).many(conn))
        assert result[0] == 1
        assert result[1] == "fish"

    def test_namedtuple(self):
        conn = mock_conn(rows=[(1, 2)], description=[("a",), ("b",)],)
        result = list(query("").returning(mapobject.namedtuple()).many(conn))
        assert result[0] == (1, 2)
        assert result[0].a == 1
        assert result[0].b == 2


class TestJoiner:
    def check_result(
        self, row_spec, join_spec, rows, positional, expected,
    ):
        row_spec = make_rowspec(row_spec, join_spec, [], positional)
        result = list(
            group_by_and_join(
                [], row_spec, join_spec, [[(item,) for item in row] for row in rows],
            )
        )
        assert result == expected

    def test_one_to_one(self):

        self.check_result(
            (MockModel, int),
            [one_to_one(MockModel, "p", int)],
            [(1, 2)],
            True,
            [MockModel(a=1, p=2)],
        )

    def test_one_to_one_with_spare_column(self):

        self.check_result(
            (int, MockModel, int),
            [one_to_one(MockModel, "p", 2)],
            [(0, 1, 2)],
            True,
            [(0, MockModel(a=1, p=2),)],
        )

        self.check_result(
            (int, MockModel, int),
            [one_to_one(MockModel, "p", 0)],
            [(0, 1, 2)],
            True,
            [(MockModel(a=1, p=0), 2)],
        )

    def test_one_to_many(self):
        self.check_result(
            (MockModel, int),
            [one_to_many(MockModel, "xs", int)],
            [(1, 2), (1, 3), (2, 1)],
            True,
            [MockModel(a=1, xs=[2, 3]), MockModel(a=2, xs=[1])],
        )

    def test_one_to_many_with_spare_column(self):
        self.check_result(
            (MockModel, int, int),
            [one_to_many(MockModel, "xs", 1)],
            [(1, 2, 3), (1, 3, 4), (2, 1, 5)],
            True,
            [(MockModel(a=1, xs=[2, 3]), 4), (MockModel(a=2, xs=[1]), 5)],
        )

    def test_one_to_many_multi_level(self):
        self.check_result(
            (MockModel, MockModel, int),
            [one_to_many(0, "xs", 1), one_to_many(1, "ys", 2)],
            [(0, 1, 2), (0, 1, 3), (0, 2, 4), (1, 5, 6)],
            True,
            [
                MockModel(a=0, xs=[MockModel(a=1, ys=[2, 3]), MockModel(a=2, ys=[4])],),
                MockModel(a=1, xs=[MockModel(a=5, ys=[6])]),
            ],
        )

    def test_it_handles_nulls_one_to_one(self):
        self.check_result(
            (MockModel, MockModel),
            [one_to_one(0, "x", 1)],
            [(0, None)],
            True,
            [MockModel(a=0, x=None)],
        )

    def test_it_handles_nulls_one_to_many(self):
        self.check_result(
            (MockModel, MockModel),
            [one_to_many(0, "xs", 1)],
            [(0, 1), (0, None)],
            True,
            [MockModel(a=0, xs=[MockModel(a=1)])],
        )

    def test_it_handles_nulls_with_intermediate_table(self):
        self.check_result(
            (MockModel, MockModel, MockModel),
            [one_to_many(0, "xs", 1), one_to_many(1, "xs", 2)],
            [(0, None, None), (0, None, 1)],
            True,
            [MockModel(a=0, xs=[])],
        )

    def test_object_labels(self):
        result = list(
            group_by_and_join(
                [],
                (
                    mapobject(MockModel, label="a", positional=True),
                    mapobject(MockModel, label="b", positional=True),
                    mapobject(MockModel, label="c", positional=True),
                ),
                [one_to_one("b", "p", "c")],
                [[(1,), (2,), (3,)]],
            )
        )
        assert result == [(MockModel(a=1), MockModel(a=2, p=MockModel(a=3)))]

    def test_multiple_independent_joins(self):
        result = list(
            group_by_and_join(
                [],
                (
                    mapobject(MockModel, label="a", positional=True),
                    mapobject(MockModel, label="b", positional=True),
                    mapobject(MockModel, label="c", positional=True),
                ),
                [one_to_many("a", "b", "b"), one_to_many("a", "c", "c")],
                [
                    [(1,), (10,), (100,)],
                    [(1,), (10,), (200,)],
                    [(1,), (20,), (100,)],
                    [(1,), (20,), (200,)],
                ],
            )
        )
        assert result == [
            MockModel(
                a=1,
                b=[MockModel(a=10), MockModel(a=20)],
                c=[MockModel(a=100), MockModel(a=200)],
            )
        ]


class TestJoinedLoads:
    def test_it_joins(self):
        class MockModelA(MockModel):
            pass

        class MockModelB(MockModel):
            pass

        conn = mock_conn([(1, 2), (1, 3)], description=[("id",), ("id",)],)
        result = list(
            query("")
            .returning(
                (MockModelA, MockModelB), [one_to_many(MockModelA, "bs", MockModelB)],
            )
            .many(conn)
        )
        assert result == [MockModelA(id=1, bs=[MockModelB(id=2), MockModelB(id=3)])]

    def test_it_handles_left_joins(self):
        conn = mock_conn([(1, None), (1, 3)], description=[("id",), ("id",)],)
        result = list(
            query("")
            .returning((MockModel, MockModel), [one_to_many(0, "items", 1)],)
            .many(conn)
        )
        assert result == [MockModel(id=1, items=[MockModel(id=3)])]

    def test_it_joins_as_dict(self):
        conn = mock_conn([(1, 2), (1, 3)], description=[("id",), ("id",)],)
        result = list(
            query("")
            .returning(
                (mapobject.dict(), mapobject.dict()), [one_to_many(0, "items", 1)],
            )
            .many(conn)
        )
        assert result == [{"id": 1, "items": [{"id": 2}, {"id": 3}]}]


def test_get_split_points_by_split():

    assert get_split_points(
        [mapobject(str), mapobject(str, split="c")], ["a", "b", "c", "d"]
    ) == [slice(0, 2), slice(2, 4)]


def test_get_split_points_by_count():

    assert get_split_points(
        [mapobject(str, column_count=3), mapobject(str)], ["a", "b", "c", "d"]
    ) == [slice(0, 3), slice(3, 4)]
