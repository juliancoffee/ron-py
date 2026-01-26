.PHONY: build clean

build:
	uv run antlr4 -Dlanguage=Python3 -o ron_parser -visitor -no-listener Ron.g4

run:
	uv run main.py

clean:
	rm -rf ron_parser/*
