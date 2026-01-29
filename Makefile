.PHONY: build clean

generated_dir=src/ron/_generated

build:
	@echo ">> cleaning the output directory"
	rm -rf $(generated_dir)/*
	@echo ">> generating parser files"
	uv run antlr4 \
		-Dlanguage=Python3 \
		-o $(generated_dir) \
		-visitor \
		-no-listener \
		Ron.g4
	@echo ">> making it a module"
	touch $(generated_dir)/__init__.py
	@echo ">> post processing"
	find $(generated_dir) -name "*.py" \
		-exec sh -c \
		'echo "# type: ignore" | cat - "{}" > "{}.tmp" && mv "{}.tmp" "{}"' \;


run:
	uv run main.py

typecheck:
	uv run mypy .

test:
	uv run pytest

clean:
	rm -rf $(generated_dir)/*
