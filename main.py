from pprint import pprint

from ron.parser import parse_ron

ron_data = r"""
Scene(
    entities: {
        "hero": Entity(
            pos: (10, 20),
            active: true,
            meta: None
        ),
        "monster": Entity(
            pos: (50, -5),
            active: false,
            meta: Some("Boss")
        )
    },
    settings: [1, 2, 3],
    id: 42
)
"""

if __name__ == "__main__":
    try:
        result = parse_ron(ron_data)

        print("--- Result Object ---")
        pprint(result)

        print("\n--- Access Check ---")
        entities = result["entities"]
        hero_meta = entities["hero"]["meta"]
        print(f"Hero Meta: {hero_meta}")

    except Exception as e:
        print(f"Error: {e}")
