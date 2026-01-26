# type: ignore

from parser import parse_ron

import pytest

from models import RonObject, RonOptional, RonStruct, RonTuple


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


def test_strings_advanced():
    obj = parse_ron(r'"Say \"Hello\""')
    assert obj.expect_str() == 'Say "Hello"'

    obj = parse_ron(r'"\u00A9 Copyright"')
    assert obj.expect_str() == "© Copyright"

    obj = parse_ron(r'r#"C:\Windows\System32"#')
    assert obj.expect_str() == r"C:\Windows\System32"


def test_strings_super_raw():
    obj = parse_ron(r'r##"Contains "# hash"##')
    assert obj.expect_str() == 'Contains "# hash'


def test_numeric_formats():
    # Hex
    assert parse_ron("0xFF").expect_int() == 255
    # Binary
    assert parse_ron("0b101").expect_int() == 5
    # Octal
    assert parse_ron("0o77").expect_int() == 63

    # Floats
    assert parse_ron("-1.5").expect_float() == -1.5
    assert parse_ron("10.0").expect_float() == 10.0


def test_trailing_commas_and_comments():
    data = r"""
    [
        1, // Перший елемент
        2, /* Другий елемент */
        3, // Кома в кінці дозволена ->
    ]
    """
    obj = parse_ron(data)

    assert obj[0].expect_int() == 1
    assert obj[2].expect_int() == 3
    assert len(obj.expect_list()) == 3


def test_map_trailing_comma():
    data = r"""
    {
        "a": 1,
        "b": 2, 
    }
    """
    obj = parse_ron(data)
    assert obj["a"].expect_int() == 1
    assert obj["b"].expect_int() == 2


def test_empty_structures():
    assert parse_ron("[]").expect_list() == ()

    obj = parse_ron("{}")
    assert len(obj.expect_map().entries) == 0

    assert parse_ron("()").expect_tuple() == RonTuple(())

    obj = parse_ron("Nothing")
    struct = obj.expect_struct()
    assert struct.name == "Nothing"
    assert struct._fields == ()


def test_type_mismatches():
    obj = parse_ron("User(age: 42)")

    with pytest.raises(ValueError, match="is not a string"):
        obj["age"].expect_str()

    with pytest.raises(ValueError, match="is not an integer"):
        obj.expect_int()

    with pytest.raises(KeyError):
        _ = obj["gender"]

    with pytest.raises(TypeError):
        _ = obj["age"][0]


def test_nested_options():
    data = "Some(Some(42))"
    obj = parse_ron(data)

    inner = obj.into_option()
    assert inner is not None

    val = inner.into_option()
    assert val is not None
    assert val.expect_int() == 42

    assert obj == RonObject(RonOptional(RonOptional(42)))


def test_option_some_none():
    data = "Some(None)"
    obj = parse_ron(data)

    inner = obj.into_option()
    assert inner is not None

    val = inner.into_option()
    assert val is None

    assert obj == RonObject(RonOptional(value=RonOptional(value=None)))
