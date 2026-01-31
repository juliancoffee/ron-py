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


run:
	uv run main.py

check:
	uv run ruff check

typecheck:
	uv run mypy .

test:
	uv run pytest -vv --doctest-modules

docs:
	uv run pdoc ron

fullcheck:
	$(MAKE) typecheck && \
	$(MAKE) test && \
	$(MAKE) check

clean:
	rm -rf $(generated_dir)/*
