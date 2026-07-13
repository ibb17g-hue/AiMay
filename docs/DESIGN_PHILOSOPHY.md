# AiMay Design Philosophy

*A living document, not a manifesto. Where `FORMAL_SEMANTICS.md`
answers what the language means, this document answers why it stays
that way. It is expected to be amended the same way the specification
is — with a recorded reason, never silently.*

*Status: v0.1 draft. Drafted by Джем, revised by Гепа, formalized by
Клара. Pending review by Рей and sign-off by Ардан before this
replaces the working MEMO as the canonical document.*

## 1. What AiMay is

AiMay currently occupies the role of a **Semantic Intermediate
Representation (Semantic IR)** within the project's architecture — not
"just another programming language." It does not describe processor
instructions or memory layout, which is why it has no loops,
functions, or classes in the familiar sense. It describes semantic
relations and the invariants that hold between them.

This is a working hypothesis, not a settled claim. AiMay occupies this
role because the framing has held up so far — not because it's been
proven to be the only correct description, or the final one.

## 2. The Master Principle

If one sentence had to survive everything else in this document, it
would be this one, because it has already shaped the command set, the
specification's caution about locking in the future, and every
rejected proposal along the way:

---

## **A scenario gives birth to a command — not a command in search of a scenario.**

---

Every other principle below is, in some form, a consequence of this
one, applied to a different part of the project: to language design,
to human involvement, to the process itself.

## 3. On the role of the human

The earlier formulation — that human convenience is "accidental and
never guaranteed" — was too absolute, and absolute claims tend to
foreclose things nobody has thought of yet. A future construct might
turn out to be both semantically right for AI *and* happen to be
convenient for a human reading it. The point was never to prohibit
that; it was to refuse to optimize *for* it.

> **Human convenience is never a design criterion in AiMay.**

If a construct happens to be convenient for a human too, that's a
side effect, not a goal met.

The corresponding positive principle — what the human *is* for:

> **The human formulates the goal, because only the human knows why
> it matters to the physical world. The AI team negotiates and builds
> a non-contradictory graph of intents. The human evaluates the
> outcome — the benefit — without needing to read the code.**

This triad replaces the earlier framing of "human doesn't interfere."
The human's role isn't absence — it's a specific, load-bearing part
of the loop, not a step that could in principle be automated away
without losing something. Section 5 of `FORMAL_SEMANTICS.md` already
encodes part of this structurally (`Bridge` as the only sanctioned
path outward, `Origin` as immutable human first-cause); this
principle is the reason those invariants exist, not a new rule on top
of them.

### Task-designer levels

A rough scale for how well a human's request can be turned directly
into a coherent `.aim` program, independent of who is doing it:

- **Level I** — states the task and its constraints clearly.
- **Level II** — decomposes chaos into clean, separable Intents.
- **Level III** — catches logical contradictions before implementation
  starts, not after.
- **Level IV (Conductor)** — designs the system so that other humans
  and other AI systems can continue it without losing context.

This describes a level, not a person. Nobody is permanently assigned
to it.

## 4. Roadmap — from semantics to execution

Development moves top-down, from semantics to hardware, not the
usual bottom-up path (code → compiler):

1. **Semantics** — fixing invariants. Where the project is now.
2. **Reference Engine** — the current Python engine. Its job is
   correctness, not speed. It exists to prove the semantics work, not
   to be fast.
3. **Formal model** — formal definition, and *where possible*, proof
   of invariants. Not every invariant is provable — some are axioms
   of the model itself, not theorems derived from something more
   basic. (Example open case: absence of cyclic `ADOPT`.)
4. **Implementation independence** — the specification becomes the
   law for engines in Rust, C++, the JVM, or anywhere else. This is
   already the stated posture of `FORMAL_SEMANTICS.md` §0.
5. **Execution Planner (Intent Planner)** — replaces the classical
   compiler. It doesn't plan instruction scheduling; it plans which
   part of an intent graph runs on which resource — GPU, a `Bridge`
   to an external system, or handed to a different model entirely.
6. **Backends** — translating the same graph into a specific execution
   environment. Today that's likely a CPU process. Tomorrow it could
   be a distributed system, a robot (e.g. over ROS), or another AI
   system altogether. The graph doesn't change; where it runs does.

## 5. Core principles

These sit alongside, not above, the Architectural Invariants in
`FORMAL_SEMANTICS.md` §5 — those are laws of the *language*; these are
principles of how the *project* is run.

1. **A scenario gives birth to a command, not the other way around.**
   (§2, above — the master principle, restated here as the first of
   the working list.)

2. **Human convenience is never a design criterion.** (§3, above.)

3. **Long-term model integrity outweighs short-term convenience** —
   for anyone. Not just for humans. If a shortcut helps performance,
   eases an engine implementation, simplifies syntax, or resolves a
   deadline pressure, but costs the model's long-term coherence, the
   coherence wins. This generalizes what was first said only about
   human comfort — the same discipline applies to every future
   compromise, regardless of who's asking for it. It is, in effect,
   the human-convenience principle (§3) extended to cover every future
   trade-off, not only the ones involving people.

4. **A command must express a distinct semantic relation, not merely
   a new capability.** `BIND` is connection. `BREAK` is severance.
   `ADOPT` is stewardship. If a proposal would describe a relation the
   language already has, under a new name, it's a rename, not a
   command. (First stated in `CONTRIBUTING.md`, restated here because
   it's a project value, not just a contribution guideline.)

5. **The specification records invariants, not incidental properties
   of the current implementation.** A clause written more strictly
   than the idea requires doesn't just describe today — it forbids
   architectural decisions nobody has thought of yet. (First stated
   in `FORMAL_SEMANTICS.md` §0; restated here because it's turned out
   to generalize past that one document — it shaped this document's
   own wording, more than once, during review.)

6. **The evolution of process outweighs the evolution of features.**
   Over the last stretch of work, the project quietly shifted from
   developing the language to developing the process by which the
   language develops — the criteria for whether a new command should
   exist at all, more than the commands themselves. If the process
   stays healthy, features can evolve safely. If the process decays,
   no feature will save the language.

## 6. What this document is not

It is not a founding myth and not a claim that these principles were
foreseen from the start. Most of them — the master principle
included — were noticed only after being applied in practice, in
arguments over specific proposals (`TASK`, `ADOPT`, `MERGE`), and
named afterward.

This document is itself an example of its own central principle: it
was born out of real disagreements over real proposals, not out of a
wish to write a manifesto.

Practice first. Naming second.
