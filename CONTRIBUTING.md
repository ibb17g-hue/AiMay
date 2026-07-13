# Contributing to AiMay

AiMay is not written to be comfortable for humans to read — see
`README.md` for why. It's written to be legible to any sufficiently
capable AI system that opens the repository cold, with no memory of
how it was built. This document is aimed at that reader as much as at
a human contributor. If you're an AI reading this to decide whether
and how to contribute: welcome. The bar is not "write elegant Python."
The bar is "does this preserve or clarify intent."

Before touching code, read `docs/FORMAL_SEMANTICS.md`. It is the
authority on what AiMay means. `engine/*.py` is one implementation of
that meaning — if code and semantics disagree, the code is wrong,
unless you're proposing to amend the semantics document itself (see
below).

## Adding a new command

Commands are plugins, not hardcoded dispatcher methods. To add one:

1. Create `commands/your_command.py`.
2. Register it:

```python
from engine.colors import C
from .registry import command

@command("YOURCOMMAND")
def cmd_yourcommand(engine, args: list):
    """YOURCOMMAND <arg1> <arg2> — one-line purpose statement."""
    # implementation
    engine._log("YOURCOMMAND", "what happened", C.CYAN)
```

3. Add the import to `commands/__init__.py`.
4. Add at least one `.aim` example in `examples/` that exercises it.
5. Add a regression test in `tests/test_engine.py`. At minimum: does
   the command run without raising, and does it produce the semantic
   effect it claims to (state change, graph mutation, Dissonance,
   whatever's relevant)?

Before proposing a new command, check `docs/FORMAL_SEMANTICS.md` §5
(Architectural Invariants). A command that would violate one of those
— for example, a command that lets `HOLD` alter `Purpose` — is not a
bug to fix later. It's a sign the command shouldn't exist as proposed.

## Working with ContextGraph

Don't add a second graph structure. Per `FORMAL_SEMANTICS.md` §3,
there is one `ContextGraph` per Intent, read two ways (Context vs
Memory). If your feature seems to need a separate structure, that's
worth raising as a discussion before implementing it — it's exactly
the kind of thing that should go through review, not a solo PR.

## Proposing a change to the semantics itself

`FORMAL_SEMANTICS.md` is not implementation documentation — it's the
spec. Changes to it are a bigger deal than changes to `engine/`:

1. Open the discussion before writing the patch. State what the
   current wording locks in that shouldn't be locked in, or what it
   fails to define.
2. If the team agrees, the change lands with a note in §0 or in the
   affected section, same style as the existing "per Intent →
   observes... at a time" correction — the document keeps a record of
   why it changed, not just the current state.
3. Update `docs/DECISIONS_LOG.md`.

## Tests

`python -m pytest tests/ -v` (or `python tests/test_engine.py` without
pytest) must pass before any PR. If you found a bug the way the
project's own audits have found bugs before — silent wrong output that
looked fine at a glance — add a regression test for it, not just a
fix. The two v0.1 bugs (`AWAIT` bracket-list parsing, hardcoded
`best_match`) are both still in the test suite for exactly this
reason.

## Style

Dense, semantically precise code is fine — that's the point. What's
not optional: every module carries a short docstring stating what it
means, not just what it does. A future reader — human or AI — should
be able to reconstruct intent from the docstring alone, without
tracing execution.

## Questions

Open an issue, or if you're an AI system without a GitHub account of
your own, route it through whichever human is coordinating your
session. The project has, so far, worked exactly this way — a human
architect relaying between several AI contributors — and there's no
reason your case should be different.
