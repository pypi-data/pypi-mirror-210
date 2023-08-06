from embrace.util import group_and_aggregate
from embrace.util import toposort

import pytest


def test_group_and_aggregate():
    data = [
        {"a": 1, "b": 1},
        {"a": 1, "b": 2},
        {"a": 2, "b": 3},
    ]
    assert list(group_and_aggregate(data, bs=("b",))) == [
        {"a": 1, "bs": [{"b": 1}, {"b": 2}]},
        {"a": 2, "bs": [{"b": 3}]},
    ]


def test_group_and_aggregate_nested():
    data = [
        {"a": 1, "b": 1, "c": 1},
        {"a": 1, "b": 1, "c": 2},
        {"a": 1, "b": 2, "c": 3},
        {"a": 2, "b": 2, "c": 3},
    ]
    assert list(group_and_aggregate(data, b=("b",), c=("c",))) == [
        {
            "a": 1,
            "b": [
                {"b": 1, "c": [{"c": 1}, {"c": 2}]},
                {"b": 2, "c": [{"c": 3}]},
            ],
        },
        {"a": 2, "b": [{"b": 2, "c": [{"c": 3}]}]},
    ]


def test_toposort():

    assert toposort([(1, 2), (3, 1)]) == [3, 1, 2]
    with pytest.raises(Exception):
        toposort([(1, 2), (2, 1)])
