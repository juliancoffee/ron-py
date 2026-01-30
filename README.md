# disclaimer
i can't guarantee the quality of this software, don't rely on it for anything serious

# what
a quick thing built with the goal to work with RON (Rust Object Notation) files in pure python

https://github.com/ron-rs/ron/issues/306

# why
because I wanted to write some scripts against RON files, and couldn't find anything usable, so I threw some code together with gemini and ANTLR4

# installation
your package manager should be able to install from git, I'll publish it on PyPi at some point
```bash
uv add git+https://github.com/juliancoffee/ron-py
```

# how to use
There's `FromRonMixin` which gives you `from_ron` method.

Or there's more low-level API if that's your thing.

Check out tests and main.py in the root.

# limitations
doesn't support extensions, yet

# contributions
PRs are probably welcome, I don't expect much in terms of the protocol, just use common sense

Ideally, we'd have some CI running first, though

# notable mentions
- https://pypi.org/project/python-ron/ & https://github.com/cswinter/pyron \
I couldn't install it, and it relies on ron-rs, which doesn't have good support for untyped data. Last I checked, it didn't support many datatype kinds (https://github.com/ron-rs/ron/issues/122).
- https://github.com/jasonjmcghee/ron-lsp just because it's cool as heck
- https://github.com/whiteand/ron-js javascript implementation
