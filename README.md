# Disclaimer
I can't guarantee the quality of this software. Don't rely on it for anything serious.

(also parts of it were made with (or by) gen-AI)

Ideally, use it if you want to hack on it, fork and/or submit PRs.

# What
A quick thing built to work with RON (Rust Object Notation) files in pure Python.

https://github.com/ron-rs/ron/issues/306

# Why
because I wanted to write some scripts against RON files, and couldn't find anything usable, so I threw some code
together with Gemini and ANTLR4.

# Installation
PyPI link: <https://pypi.org/project/ron-python/>
```bash
pip install ron-python
```
Or with a modern alternative:
```bash
uv add ron-python
```
Or, if you want a development version, feel free to use something like that:
```bash
uv add git+https://github.com/juliancoffee/ron-py
```
I'd recommend pinning it to a specific commit, though:
```bash
uv add git+https://github.com/juliancoffee/ron-py.git@8ba6bd6
```

# How to use
Stable docs: <https://juliancoffee.github.io/ron-py/latest/ron.html> \
Main branch docs: <https://juliancoffee.github.io/ron-py/dev/ron.html>

There's `FromRonMixin` which gives you `from_ron` method.
```python
from dataclasses import dataclass
from ron import FromRonMixin

@dataclass
class Click(FromRonMixin):
  x: int
  y: int

obj = Click.from_ron("Click(x: 10, y: 20)")
assert isinstance(res1, Click)
assert res1.x == 10
```
Or there's more low-level API if that's your thing.
```python
from ron import parse_ron
from ron.models import RonStruct

def test_struct_as_key():
    data = r"""
    {
        UserID(123): "Admin",
        UserID(456): "Guest"
    }
    """
    # yes, you can just parse it to a raw object
    obj = parse_ron(data)

    # type-narrow it
    raw_map = obj.expect_map()
    assert len(raw_map.entries) == 2

    keys = list(raw_map.entries.keys())
    target_key = keys[0]
    # or compare to internal types
    # sneak peek, we also have spans (only for struct field values though, as of now)
    # use `parse_ron(src, with_spans=True)`
    assert target_key == RonStruct("UserID", (123,), spans=None)
    assert raw_map.entries[target_key] == "Admin"
```
Alternatively, there's `__getitem__` implementation, which loses some type strictness, but is super convenient.
```python
def test_deep_chaining_nested_structures():
    ron_str = """
        Player(
            stats: { "attributes": [10, 15] },
            inventory: [ Item(name: "Sword") ]
        )
    """
    obj = parse_ron(ron_str)

    # use a struct like you'd use dict
    strength = obj["stats"]["attributes"][0]
    assert strength.expect_int() == 10

    # can be infinitely nested, until you jump out with `expect_*` method
    weapon = obj["inventory"][0]["name"]
    assert weapon.expect_str() == "Sword"

def test_unit_struct_lookup():
    obj = parse_ron('{ King: "Crown" }')

    # or even go bonkers and do this
    assert obj["King"].expect_str() == "Crown"
```

Check out tests and main.py in the root for more (and, potentially, more up-to-date examples).

# Limitations
Doesn't support extensions, yet.

# Contributions
PRs are probably welcome, I don't expect much in terms of the protocol, just use common sense

We even have CI now :D

# Notable mentions
- https://pypi.org/project/python-ron/ & https://github.com/cswinter/pyron \
I couldn't install it, and it relies on ron-rs, which doesn't have good support for untyped data. Last I checked, it didn't support many datatype kinds (https://github.com/ron-rs/ron/issues/122).
- https://github.com/jasonjmcghee/ron-lsp just because it's cool as heck
- https://github.com/whiteand/ron-js javascript implementation
- https://github.com/chriskilding/jackson-dataformat-ron Java Jackson implementation
- https://github.com/sorairolake/ron-wasm and wasm bindings, which probably suffer from the same problem as python bindings
- https://github.com/ron-rs/ron2 ron rewrite to fix the current issues by relying less on serde
