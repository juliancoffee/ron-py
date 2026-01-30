# type: ignore
from ron import parse_ron


def test_struct_field_spans():
    data = """\
MyStruct(a: 100)
"""
    val = parse_ron(data, with_spans=True).expect_struct()

    a_span = val.spans["a"]

    # indices from 12 to 14
    assert a_span[0].ch == 12
    assert a_span[1].ch == 14

    # line numbers, start from 1
    assert a_span[0].line == 1
    assert a_span[1].line == 1

    # column numbers, start from 1
    assert a_span[0].column == 13
    assert a_span[1].column == 15


def test_multiline_struct_spans():
    data = """\
(
field: "multi
    line"
)
"""
    val = parse_ron(data, with_spans=True).expect_struct()

    span = val.spans["field"]

    assert span[0].line == 2
    assert span[1].line == 3

    assert span[0].column == 8
    assert span[1].column == 9


def test_nested_oneliner():
    data = """\
Outer(inner: Inner(field: 123))
"""
    val = parse_ron(data, with_spans=True).expect_struct()

    inner_struct = val._fields["inner"]
    inner_span = val.spans["inner"]

    assert inner_span[0].ch == 13
    assert inner_span[0].line == 1

    assert inner_span[0].column == 14
    assert inner_span[1].column == 30

    field_span = inner_struct.spans["field"]
    assert field_span[0].column == 27
    assert field_span[1].column == 29
