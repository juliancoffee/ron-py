from ron import parse_ron


def test_struct_access_happy_path():
    obj = parse_ron(
        'GameConfig(width: 1920, title: "Super Ron", is_fullscreen: true)'
    )

    assert obj["width"].expect_int() == 1920
    assert obj["title"].expect_str() == "Super Ron"
    assert obj["is_fullscreen"].expect_bool() is True


def test_tuple_struct_indexing():
    obj = parse_ron("Point3(10, 20, 30)")

    assert obj[0].expect_int() == 10
    assert obj[1].expect_int() == 20
    assert obj[2].expect_int() == 30


def test_list_and_seq_indexing():
    obj = parse_ron("[100, 200, 300]")

    assert obj[0].expect_int() == 100
    assert obj[2].expect_int() == 300

    seq = obj.expect_list()
    assert len(seq.as_tuple) == 3


def test_map_string_lookup():
    obj = parse_ron('{ "hp": 100, "mana": 50 }')

    assert obj["hp"].expect_int() == 100
    assert obj["mana"].expect_int() == 50

    _ = obj.expect_map()


def test_deep_chaining_nested_structures():
    ron_str = """
        Player(
            stats: { "attributes": [10, 15] },
            inventory: [ Item(name: "Sword") ]
        )
    """
    obj = parse_ron(ron_str)

    strength = obj["stats"]["attributes"][0]
    assert strength.expect_int() == 10

    weapon = obj["inventory"][0]["name"]
    assert weapon.expect_str() == "Sword"


def test_edge_case_map_with_integer_keys():
    obj = parse_ron('{ 1: "Level 1", 5: "Level 5" }')

    assert obj[1].expect_str() == "Level 1"
    assert obj[5].expect_str() == "Level 5"


def test_struct_as_map_key():
    obj = parse_ron("""{ 
        Coordinate(x: 10, y: 10): "Base",
        Coordinate(x: 20, y: 20): "Outpost"
    }""")

    key_struct = parse_ron("Coordinate(x: 10, y: 10)").expect_struct()

    assert obj[key_struct].expect_str() == "Base"


def test_enum_variant_access():
    obj = parse_ron("[ Circle(radius: 5.5), Rect(10, 20) ]")

    circle = obj[0]
    assert circle["radius"].expect_float() == 5.5

    rect = obj[1]
    assert rect[0].expect_int() == 10
    assert rect[1].expect_int() == 20


def test_pyindex_tuple_keys():
    obj = parse_ron('{ (0, 0): "Origin", (1, 2): "Target" }')

    assert obj[(0, 0)].expect_str() == "Origin"
    assert obj[(1, 2)].expect_str() == "Target"


def test_ergonomic_map_lookup():
    obj = parse_ron('{ {"id": 1}: "Meta" }')

    assert obj[{"id": 1}].expect_str() == "Meta"


def test_ergonomic_struct_lookup_via_dict():
    obj = parse_ron('{ User(id: 1): "Admin" }')

    assert obj[{"id": 1}].expect_str() == "Admin"


def test_ergonomic_list_lookup():
    obj = parse_ron('{ [1, 2]: "Sequential" }')

    assert obj[[1, 2]].expect_str() == "Sequential"


def test_unnamed_struct_lookup_via_dict():
    obj = parse_ron('{ (id: 1): "Admin" }')

    assert obj[{"id": 1}].expect_str() == "Admin"


def test_struct_unnamed_lookup_via_dict():
    obj = parse_ron('{ User(1): "Admin" }')

    assert obj[(1,)].expect_str() == "Admin"


def test_unnamed_struct_lookup():
    obj = parse_ron('{ (x: 10, y: 20): "Origin" }')

    assert obj[{"x": 10, "y": 20}].expect_str() == "Origin"


def test_named_struct_unnamed_fields_lookup():
    obj = parse_ron('{ Point(10, 20): "Target" }')

    assert obj[(10, 20)].expect_str() == "Target"


def test_unit_struct_lookup():
    obj = parse_ron('{ King: "Crown" }')

    assert obj["King"].expect_str() == "Crown"


def test_optional_lookup():
    obj = parse_ron('{ Some("King"): "Crown", None: "Hat" }')

    assert obj["King"].expect_str() == "Crown"
    assert obj[None].expect_str() == "Hat"


def test_optional_struct_lookup():
    obj = parse_ron('{ Some(King): "Crown", None: "Hat" }')

    # this doesn't quite work, for now
    # assert obj["King"].expect_str() == "Crown"
    assert obj[None].expect_str() == "Hat"


def test_reversed_optional_lookup():
    obj = parse_ron('{ None: "Hat", Some("King"): "Crown" }')

    assert obj["King"].expect_str() == "Crown"
    assert obj[None].expect_str() == "Hat"


def test_parsed_optional_struct_lookup():
    obj = parse_ron('{ Some(King): "Crown", None: "Hat" }')

    assert obj[parse_ron("Some(King)")].expect_str() == "Crown"


def test_iteration_lookup():
    # edge case, getitem also implements iter using range() keys
    #
    # and no, we won't support that for maps
    # not now, at least
    obj = parse_ron("[100, 200, 300]")

    # yeah, mypy doesn't know about that, which is probably good
    assert [x.expect_int() for x in obj] == [100, 200, 300]  # type: ignore


def test_field_iteration_lookup():
    obj = parse_ron("(x: [100, 200, 300])")

    # yeah, mypy doesn't know about that, which is probably good
    assert [x.expect_int() for x in obj["x"]] == [100, 200, 300]  # type: ignore
