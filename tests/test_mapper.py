from dataclasses import dataclass
from typing import Optional

import pytest

from ron.mapper import convert_ron
from ron.parser import parse_ron


def test_ui_action_enum():
    class Action:
        pass

    @dataclass
    class Click(Action):
        x: int
        y: int

    @dataclass
    class KeyPress(Action):
        key: str

    obj1 = parse_ron("Click(x: 10, y: 20)")
    res1 = convert_ron(obj1.v, Action)
    assert isinstance(res1, Click)
    assert res1.x == 10

    obj2 = parse_ron('KeyPress(key: "Enter")')
    res2 = convert_ron(obj2.v, Action)
    assert isinstance(res2, KeyPress)
    assert res2.key == "Enter"


def test_ml_optimizer_hierarchy():
    class Optimizer:
        pass

    @dataclass
    class SGD(Optimizer):
        learning_rate: float
        momentum: float

    @dataclass
    class Adam(Optimizer):
        learning_rate: float
        beta1: float
        beta2: float

    @dataclass
    class TrainingConfig:
        opt: Optimizer
        epochs: int

    data = """
TrainingConfig(
    opt: Adam(learning_rate: 0.001, beta1: 0.9, beta2: 0.999),
    epochs: 10,
)
    """
    obj = parse_ron(data)
    cfg = convert_ron(obj.v, TrainingConfig)

    assert isinstance(cfg.opt, Adam)
    assert cfg.opt.beta1 == 0.9
    assert cfg.epochs == 10

    data = """
TrainingConfig(
    opt: SGD(learning_rate: 1e-4, momentum: 1e-4),
    epochs: 10,
)
    """
    obj = parse_ron(data)
    cfg = convert_ron(obj.v, TrainingConfig)

    assert isinstance(cfg.opt, SGD)
    assert cfg.opt.learning_rate == 0.0001
    assert cfg.epochs == 10


def test_nested_optional_entities():
    class EntityType:
        pass

    @dataclass
    class Monster(EntityType):
        hp: int
        aggressiveness: float

    @dataclass
    class Item(EntityType):
        name: str
        value: int

    @dataclass
    class WorldNode:
        id: int
        entity: Optional[EntityType]
        neighbors: list[int]

    data_some = """
WorldNode(
    id: 1,
    entity: Some(Monster(hp: 100, aggressiveness: 0.5)),
    neighbors: [2, 3]
)
"""
    res_some = convert_ron(parse_ron(data_some).v, WorldNode)
    assert isinstance(res_some.entity, Monster)
    assert res_some.neighbors == [2, 3]

    data_none = "WorldNode(id: 2, entity: None, neighbors: [])"
    res_none = convert_ron(parse_ron(data_none).v, WorldNode)
    assert res_none.entity is None
    assert res_none.neighbors == []

    data_some = """
WorldNode(
    id: 1,
    entity: Some(Item(name: "Sword", value: 100)),
    neighbors: [2, 3]
)
"""
    res_some = convert_ron(parse_ron(data_some).v, WorldNode)
    assert isinstance(res_some.entity, Item)
    assert res_some.entity.name == "Sword"
    assert res_some.entity.value == 100
    assert res_some.neighbors == [2, 3]


def test_tuple_struct_mapping():
    @dataclass
    class Color:
        r: int
        g: int
        b: int

    obj = parse_ron("Color(255, 128, 64)")
    res = convert_ron(obj.v, Color)

    assert res.r == 255
    assert res.g == 128
    assert res.b == 64


def test_mapping_errors():
    @dataclass
    class User:
        name: str

    obj_wrong_name = parse_ron('Admin(name: "Bob")')
    with pytest.raises(ValueError, match="Name mismatch"):
        convert_ron(obj_wrong_name.v, User)

    class Base:
        pass

    obj_unknown = parse_ron("UnknownStruct(val: 1)")
    with pytest.raises(ValueError, match="No subclass found"):
        convert_ron(obj_unknown.v, Base)
