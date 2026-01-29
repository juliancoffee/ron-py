from dataclasses import dataclass

from ron import FromRonMixin


def test_mixin_simple_struct():
    @dataclass
    class Player(FromRonMixin):
        username: str
        level: int
        inventory: list[str]

    ron_data = """
        (
            username: "Leeroy",
            level: 60,
            inventory: ["Chicken", "Sword"],
        )
    """

    p = Player.from_ron(ron_data)

    assert isinstance(p, Player)
    assert p.username == "Leeroy"
    assert p.level == 60
    assert p.inventory == ["Chicken", "Sword"]


def test_mixin_inheritance_check():
    @dataclass
    class A(FromRonMixin):
        x: int

    @dataclass
    class B(FromRonMixin):
        y: int

    obj_a = A.from_ron("(x: 1)")
    obj_b = B.from_ron("(y: 2)")

    assert isinstance(obj_a, A)
    assert not isinstance(obj_a, B)
    assert obj_a.x == 1

    assert isinstance(obj_b, B)
    assert obj_b.y == 2


def test_game_config_mapping():
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

    assert isinstance(config, GameConfig)
    assert config.window_size == (800, 600)
    assert config.window_title == "PAC-MAN"
    assert config.fullscreen is False
    assert config.mouse_sensitivity == 1.4

    assert isinstance(config.key_bindings, dict)
    assert isinstance(config.key_bindings["up"], Up)
    assert isinstance(config.key_bindings["left"], Left)

    assert isinstance(config.difficulty_options, DifficultyOptions)
    assert isinstance(config.difficulty_options.start_difficulty, Easy)
    assert config.difficulty_options.adaptive is False
    assert config.difficulty_options.start_difficulty == Easy()
