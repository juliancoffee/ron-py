from parser import parse_ron

import pytest


def test_primitives():
    assert parse_ron("42").expect_int() == 42
    assert parse_ron("-3.14").v == -3.14  # Можна і через .v
    assert parse_ron("true").expect_bool() is True
    assert parse_ron('"hello"').expect_str() == "hello"


def test_named_struct():
    data = 'User(id: 101, active: true, name: "Coffee")'
    obj = parse_ron(data)

    assert obj["id"].expect_int() == 101
    assert obj["active"].expect_bool() is True
    assert obj["name"].expect_str() == "Coffee"


def test_nested_access():
    data = r"""
    Server(
        config: Config(
            ports: [80, 443]
        )
    )
    """
    obj = parse_ron(data)

    port = obj["config"]["ports"][1]
    assert port.expect_int() == 443


def test_maps_and_tuples():
    data = '{ "coords": (10, 20) }'
    obj = parse_ron(data)

    x = obj["coords"][0].expect_int()
    y = obj["coords"][1].expect_int()

    assert x == 10
    assert y == 20


def test_options():
    data = 'Container(item: Some("Sword"), empty: None)'
    obj = parse_ron(data)

    item = obj["item"].into_option()
    assert item is not None
    assert item.expect_str() == "Sword"

    empty = obj["empty"].into_option()
    assert empty is None


def test_missing_key():
    obj = parse_ron("Box(val: 1)")

    with pytest.raises(KeyError):
        _ = obj["wrong_key"]
