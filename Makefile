.PHONY: build clean

build:
	uv run antlr4 -Dlanguage=Python3 -o ron_parser -visitor -no-listener Ron.g4
	touch ron_parser/__init__.py
	find ./ron_parser -name "*.py" \
		-exec sh -c \
		'echo "# type: ignore" | cat - "{}" > "{}.tmp" && mv "{}.tmp" "{}"' \;


run:
	uv run main.py

typecheck:
	uv run mypy .

test:
	uv run pytest tests.py

clean:
	rm -rf ron_parser/*
