# disclaimer
i can't guarantee the quality of this software, don't rely on it for anything serious

# what
a quick thing build with the goal to work with RON (Rust Object Notation) files in pure python

# why
because I wanted to write some scripts against RON files, and couldn't find anything usable, so I threw some code together with gemini and ANTLR4

# installation
your package manager should be able to install from git, I'll publish it on PyPi at some point

# how to use
There's `FromRonMixin` which gives you `from_ron` method.

Or there's more low-level API if that's your thing

# limitations
doesn't support extensions, yet

# contributions
PRs are probably welcome, I don't expect much in terms of the protocol, just use the common sense

Ideally, we'd have some CI running first though
