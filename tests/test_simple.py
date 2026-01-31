import pytest

from ron.models import (
    RonChar,
    RonMap,
    RonObject,
    RonOptional,
    RonSeq,
    RonStruct,
)
from ron.parser import parse_ron


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

    item = obj["item"].maybe()
    assert item is not None
    assert item.expect_str() == "Sword"

    empty = obj["empty"].maybe()
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
    assert type(start_key) is RonSeq
    assert start_key == RonSeq((0, 0), kind="tuple")
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
    assert target_key == RonStruct("UserID", (123,), spans=None)
    assert raw_map.entries[target_key] == "Admin"


def test_enum_as_key():
    data = r"""
    {
        Red: "Color Red",
        Green: "Color Green"
    }
    """
    obj = parse_ron(data)
    entries = obj.expect_map().entries

    red_key = next(
        k
        for k in entries.keys()
        if isinstance(k, RonStruct) and k.name == "Red"
    )

    assert entries[red_key] == "Color Red"


def test_deeply_nested_key():
    data = '{ Key(zone: "A", id: 1): true }'

    obj = parse_ron(data)
    entry_key = list(obj.expect_map().entries.keys())[0]

    assert isinstance(entry_key, RonStruct)
    assert entry_key.name == "Key"
    assert entry_key.as_dict["zone"] == "A"
    assert obj[entry_key].expect_bool() is True


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


def test_raw_strings_multiple_hashes():
    cases = [
        (r'r"simple raw"', "simple raw"),
        (r'r#"one hash"#', "one hash"),
        (r'r##"two hashes"##', "two hashes"),
        (r'r###"three hashes"###', "three hashes"),
        (r'r####"four hashes"####', "four hashes"),
    ]
    for data, expected in cases:
        assert parse_ron(data).expect_str() == expected


def test_raw_strings_complex_content():
    data = r'r##"Тут є "# одна решітка та ##"##'
    assert parse_ron(data).expect_str() == 'Тут є "# одна решітка та ##'

    data = r"""r#"Line 1
Line 2"#"""
    assert parse_ron(data).expect_str() == "Line 1\nLine 2"


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
    assert len(obj.expect_list().as_tuple) == 3


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
    assert parse_ron("[]").expect_list().as_tuple == ()

    obj = parse_ron("{}")
    assert len(obj.expect_map().entries) == 0

    assert parse_ron("()").expect_tuple().as_tuple == ()

    obj = parse_ron("Nothing")
    struct = obj.expect_struct()
    assert struct.name == "Nothing"
    assert struct._fields == ()


def test_anon_struct():
    obj = parse_ron("""
    // comment comment
    (
        a: Item("path.to.item"),
        b: Item("path.to.other.item"),
    )
    """)
    struct = obj.expect_struct()
    assert struct.name is None
    assert struct.as_dict["a"] == RonStruct(
        "Item", ("path.to.item",), spans=None
    )
    assert struct.as_dict["b"] == RonStruct(
        "Item", ("path.to.other.item",), spans=None
    )
    assert len(struct._fields) == 2


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

    inner = obj.maybe()
    assert inner is not None

    val = inner.maybe()
    assert val is not None
    assert val.expect_int() == 42

    assert obj == RonObject(RonOptional(RonOptional(42)))


def test_option_some_none():
    data = "Some(None)"
    obj = parse_ron(data)

    inner = obj.maybe()
    assert inner is not None

    val = inner.maybe()
    assert val is None

    assert obj == RonObject(RonOptional(value=RonOptional(value=None)))


def test_scientific_notation():
    assert parse_ron("1.2e4").v == 12000.0
    assert parse_ron("5e-2").v == 0.05
    assert parse_ron("1e+3").v == 1000.0
    assert parse_ron(".5").v == 0.5
    assert parse_ron("42.").v == 42.0


def test_char_literals():
    assert parse_ron("'a'").v == RonChar("a")
    assert parse_ron("'z'").v == RonChar("z")

    assert parse_ron(r"'\n'").v == RonChar("\n")
    assert parse_ron(r"'\t'").v == RonChar("\t")
    assert parse_ron(r"'\''").v == RonChar("'")

    assert parse_ron(r"'\u00AC'").v == RonChar("\u00ac")


def test_multiline_strings():
    data = """
    "First line
    Second line
    Third line"
    """
    obj = parse_ron(data)
    assert obj.expect_str() == "First line\n    Second line\n    Third line"


def test_deep_nesting_complex():
    data = r"""
    Some([
        {
            (1, 2): User(
                id: Some(42),
                tags: ["rust", "python"],
            ),
        },
    ])
    """
    obj = parse_ron(data)

    # Розгортаємо "матрьошку"
    inner_list = obj.maybe()
    assert inner_list is not None

    first_map = inner_list[0]

    raw_map = first_map.v
    assert isinstance(raw_map, RonMap)

    key = list(raw_map.entries.keys())[0]
    assert isinstance(key, RonSeq)
    assert key.elements == (
        1,
        2,
    )

    user = first_map[key]
    user_id = user["id"].maybe()

    assert user_id is not None
    assert user_id.expect_int() == 42
    assert user["tags"][1].expect_str() == "python"


def test_empty_with_comments():
    # and I guess this tests unicode, lol

    map_data = "{ /* коментар */ }"
    list_data = "[ // порожньо \n ]"
    tuple_data = "( \n /* нічого */ \n )"

    assert len(parse_ron(map_data).expect_map().entries) == 0
    assert parse_ron(list_data).expect_list().as_tuple == ()
    assert parse_ron(tuple_data).expect_tuple().as_tuple == ()


def test_no_whitespace_parsing():
    data = "[{1:User(id:1),2:User(id:2)},[Some(1),None]]"

    obj = parse_ron(data)

    map_part = obj[0]
    entries = map_part.expect_map().entries
    assert 1 in entries

    user1 = map_part[1]
    assert user1.expect_struct().name == "User"
    assert user1["id"].expect_int() == 1

    list_part = obj[1]
    x = list_part[0].maybe()
    assert x is not None
    assert x.expect_int() == 1
    assert list_part[1].maybe() is None


def test_dense_scientific_notation():
    data = '{"val":-1.2e4,"next":.5}'
    obj = parse_ron(data)

    assert obj["val"].v == -12000.0
    assert obj["next"].v == 0.5
