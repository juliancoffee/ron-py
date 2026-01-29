"""
Example of an API
"""

from dataclasses import dataclass
from pprint import pprint

# mixin is for high-level api, returns your class
# parse_ron is for low-level api, returns internal ron object
# from_ron is a middle ground, you can use for any dataclass
from ron import FromRonMixin, parse_ron


# direction enums
class Direction:
    pass


@dataclass
class Up(Direction):
    pass


@dataclass
class Down(Direction):
    pass


@dataclass
class Left(Direction):
    pass


@dataclass
class Right(Direction):
    pass


# difficulty enums
class Difficulty:
    pass


@dataclass
class Easy(Difficulty):
    pass


@dataclass
class Hard(Difficulty):
    pass


# difficulty options struct (anonymous in the source)
@dataclass
class DifficultyOptions:
    start_difficulty: Difficulty
    adaptive: bool


# top-level config
@dataclass
class GameConfig(FromRonMixin):
    window_size: tuple[int, int]
    window_title: str
    fullscreen: bool
    mouse_sensitivity: float
    key_bindings: dict[str, Direction]
    difficulty_options: DifficultyOptions


ron_input = """
GameConfig(
    window_size: (800, 600),
    window_title: "PAC-MAN",
    fullscreen: false,

    mouse_sensitivity: 1.4,
    key_bindings: {
        "up": Up,
        "down": Down,
        "left": Left,
        "right": Right,

        // Uncomment to enable WASD controls
        /*
        "W": Up,
        "S": Down,
        "A": Left,
        "D": Right,
        */
    },

    // See? Struct names are optional
    difficulty_options: (
        start_difficulty: Easy,
        adaptive: false,
    ),
)
"""

config = GameConfig.from_ron(ron_input)
pprint(config)

print("Low-level API")
obj = parse_ron(ron_input)
# knows nothing about the class, just responds to the input
#
# you can use expect_* methods to narrow the type
# structs can have named or unnamed fields, hence as_dict/as_tuple
print(obj.expect_struct().as_dict["window_size"])
# or use getitem api and only narrow at the end
print(obj["key_bindings"]["down"].expect_struct())
# or even use raw values
