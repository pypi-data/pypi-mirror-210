from unittest.mock import call
from unittest.mock import Mock
import pytest
from embrace import exceptions
from embrace import pool
from embrace import poolvalidators


class TestPool:
    def test_it_gets_a_connection(self):
        conn = Mock()
        p = pool.ConnectionPool(lambda: conn)
        assert p.getconn() is conn

    def test_it_releases_a_connection(self):
        conn = Mock()
        p = pool.ConnectionPool(lambda: conn)
        p.release(p.getconn())
        assert conn.rollback.mock_calls == [call()]

    def test_it_validates_a_connection(self):
        conn = Mock()
        validator = Mock(spec=poolvalidators.ConnectionValidator)
        p = pool.ConnectionPool(lambda: conn, validator=validator)
        assert p.getconn() is conn
        assert validator.validate.mock_calls == [call(conn)]
        p.release(conn)
        assert validator.before_release.mock_calls == [call(conn)]

    def test_it_limits_connections(self):
        conn = Mock()
        p = pool.ConnectionPool(lambda: conn, limit=1, timeout=0.01)
        assert p.getconn() is conn
        with pytest.raises(exceptions.ConnectionLimitError):
            p.getconn()

    def test_releasing_connections_makes_them_available_again(self):
        conn = Mock()
        p = pool.ConnectionPool(lambda: conn, limit=1, timeout=0.01)
        assert p.getconn() is conn
        p.release(conn)
        assert p.getconn() is conn

    def test_it_works_as_a_context_manager(self):
        conn = Mock()
        p = pool.ConnectionPool(lambda: conn, limit=1, timeout=0.01)
        with p.connect() as c:
            assert c is conn
