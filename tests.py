# type: ignore

from parser import parse_ron

import pytest

from models import RonStruct, RonTuple


def test_primitives():
    assert parse_ron("42").expect_int() == 42
    assert parse_ron("-3.14").expect_float() == -3.14
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


def test_tuple_as_key():
    data = r"""
    {
        (0, 0): "Start",
        (10, 20): "Finish"
    }
    """
    obj = parse_ron(data)

    raw_map = obj.expect_map()
    assert len(raw_map.entries) == 2

    keys = list(raw_map.entries.keys())

    start_key = keys[0]
    assert type(start_key) is RonTuple
    assert start_key == RonTuple((0, 0))
    assert raw_map.entries[start_key] == "Start"


def test_struct_as_key():
    data = r"""
    {
        UserID(123): "Admin",
        UserID(456): "Guest"
    }
    """
    obj = parse_ron(data)
    raw_map = obj.expect_map()
    assert len(raw_map.entries) == 2

    keys = list(raw_map.entries.keys())
    target_key = keys[0]
    assert target_key == RonStruct("UserID", (123,))
    assert raw_map.entries[target_key] == "Admin"


def test_enum_as_key():
    data = r"""
    {
        Red: "Color Red",
        Green: "Color Green"
    }
    """
    obj = parse_ron(data)
    entries = obj.v.entries

    red_key = next(
        k
        for k in entries.keys()
        if isinstance(k, RonStruct) and k.name == "Red"
    )

    assert entries[red_key] == "Color Red"


def test_deeply_nested_key():
    data = '{ Key(zone: "A", id: 1): true }'

    obj = parse_ron(data)
    entry_key = list(obj.v.entries.keys())[0]

    assert isinstance(entry_key, RonStruct)
    assert entry_key.name == "Key"
    assert entry_key._fields["zone"] == "A"
    assert obj.v.entries[entry_key] is True
