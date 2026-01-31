"""
Python implementation of Rusty Object Notation (RON).

See: <https://docs.rs/ron/latest/ron/>

This package allows working with RON data in two ways:
1. Strict Mapping: Deserializing RON directly into Python dataclasses and Enums.
2. Dynamic Access: Traversing the raw data structure using a
`ron.models.RonObject`.

Well, and direct AST access, using `ron.models.RonValue`.

Quickstart
---

You'll most probably use a `FromRonMixin` mixin to bind RON data to typed
Python definitions:

>>> from dataclasses import dataclass
>>> from ron import FromRonMixin
>>>
>>> # 1. Define Enums (variants) using inheritance
>>> class Difficulty: pass
>>>
>>> @dataclass
... class Easy(Difficulty): pass
>>> @dataclass
... class Hard(Difficulty): pass
>>> @dataclass
... class Custom(Difficulty):
...     factor: float
>>>
>>> # 2. Define schema
>>> @dataclass
... class GameConfig(FromRonMixin):
...     title: str
...     difficulty: Difficulty
>>>
>>> # 3. Load from RON
>>> ron_data = '''
...     GameConfig(
...         title: "Dungeon Crawler",
...         difficulty: Easy,
...     )
... '''
>>> config = GameConfig.from_ron(ron_data)
>>> config.title
'Dungeon Crawler'
>>> config.difficulty
Easy()

And yes, unlike traditional python enums, RON enums can have data attached to
them.
>>> ron_data = '''
...     GameConfig(
...         title: "Dungeon Crawler",
...         difficulty: Custom(0.7),
...     )
... '''
>>> config = GameConfig.from_ron(ron_data)
>>> config.difficulty
Custom(factor=0.7)

Dynamic Access
---

If you do not have a strict schema, use `parse_ron` to get a `RonObject` wrapper.
It abstracts away specific key types (allowing string/tuple lookups) and provides
type-checked accessors.

>>> from ron import parse_ron
>>> obj = parse_ron('(config: (resolution: (1920, 1080)))')
>>> # Access nested fields using standard Python keys
>>> obj["config"]["resolution"][0].expect_int()
1920

Parser API
---
`parse_ron` produces an immutable tree (wrapped into `ron.models.RonObject`)
of:
* `ron.models.RonStruct` (includes span information for error reporting)
* `ron.models.RonMap`
* `ron.models.RonSeq`
* `ron.models.RonOptional`
* Primitives (`int`, `float`, `str`, `bool`, `ron.models.RonChar`)

Known limitations
---
Extensions are not implemented yet.

Reference
---
"""

from ron.mapper import FromRonMixin, from_ron
from ron.parser import parse_ron

__all__ = ["models", "parse_ron", "from_ron", "FromRonMixin"]
