# Formal Semantics of AiMay

*Status: draft v0.1 — team-approved by Ardan, Clara, Hepa; pending Джем's
review against `PROTOCOL_OF_INTENT.md` archive.*

This document does not describe how the current Python engine works.
`engine/*.py` is one implementation of what follows — the semantics
below are meant to hold regardless of whether AiMay is ever
re-implemented in Rust, on the JVM, or anywhere else. Where the
current implementation diverges from this spec, the implementation is
what's wrong, not the spec — unless the spec itself is amended.

## 0. On writing this document

*A specification records the present and, in the same act, licenses
the future. When a clause is written more strictly than the idea
actually requires, it doesn't just describe today's implementation —
it forbids architectural decisions nobody has thought of yet. The
discipline this document tries to hold to is: capture invariants, not
incidental properties of the current engine.*

One working phrase for that discipline, offered mid-review and worth
keeping visible:

> Architecture should be maximally strict about meaning and maximally
> permissive about future implementation.

Section 3's original wording — "exactly one graph *per* Intent" —
is the concrete example this document keeps for itself as a reminder
of what happens when that discipline slips.

## 1. Intent

An Intent is the atomic unit of an AiMay program. Formally:

```
Intent =
    Purpose   — the declared reason this Intent exists; immutable once DECL'd
    Origin    — the first-cause author of the Intent; immutable for its lifetime
    Metric    — the condition under which Purpose counts as fulfilled
    State     — current position in the Intent lifecycle (§2)
    Graph     — a single ContextGraph, interpreted two ways (§3)
    Bonds     — the set of (a, b, locked) edges created by BIND
```

`Purpose` and `Origin` are write-once. No command in the current
command set is permitted to alter them after `DECL`. This is not an
implementation detail — it's what makes an Intent *this* Intent rather
than a new one. If Purpose needs to change, the correct operation is
`SUPERSEDE`, not mutation.

## 2. Lifecycle — the Intent state machine

```
            DECL
             │
             ▼
         [Declared] ── (implicit, same tick) ──▶ [Active]
                                                     │
                             ┌───────────────────────┼───────────────────────┐
                             ▼                        ▼                       ▼
                       [Fulfilled]              [Suspended]             [Superseded]
                        (via SEAL)          (awaiting external      (a newer Intent
                                              conditions; may            replaces this
                                              re-enter Active)             one's Purpose)
```

Four states. That's the whole automaton at the Intent level.

`AWAIT`, `CHECK`, `BIND`, `FORK`, `TUNE`, `HOLD` are **not** states —
they are phases of execution that occur *inside* `Active`. **An Intent
that is waiting on a signal via `AWAIT` is still, formally, `Active`;
it has not entered some fifth state called `Awaiting`.** This matters
for one concrete reason: `SEAL` is only a formal error if called on an
Intent that is not `Active` — it is never blocked merely because an
`AWAIT` or `BIND` phase happens to be mid-flight.

Any command that reaches an unresolvable Dissonance while an Intent is
`Active` moves it to `Suspended`, not `Superseded` — `Superseded`
requires a second, later Intent that explicitly claims to replace the
first one's Purpose. An Intent cannot supersede itself.

`TASK` adds one gating rule on top of this automaton, not a new
state: an Intent with unresolved `TASK` children (children whose
status is neither `Fulfilled` nor `Suspended`) cannot transition
`Active → Fulfilled` via `SEAL`. Every other command — `EMIT`, `CHECK`,
`BIND`, `HOLD`, and so on — continues to operate normally while
children are pending; the parent remains fully `Active` in every
other respect. Only the `SEAL` transition is blocked. (Decision №18.)

## 3. ContextGraph — one structure, two interpretations

Every Intent operates through exactly one ContextGraph at a time. That
graph is not split into a "memory graph" and a "context graph" as
separate data structures. Instead, the same `ContextGraph` is read two
different ways depending
on which command is asking:

- **Context** — the *current slice* of the graph: which nodes are
  reachable right now, at what trust, from the Intent's own node.
  This is what `CHECK`, `BIND`, and resonance queries (`FORK`) operate
  on. It is inherently time-sensitive, because trust decays.
- **Memory** — the *historical layer* of the same graph: every node
  ever written via `HOLD`, whether or not it's still above the trust
  threshold that would make it relevant to a live `CHECK`. Memory
  doesn't forget; it just stops being trusted.

If a future version of the language finds that the algorithms serving
these two interpretations genuinely conflict — for instance, if
Memory needs append-only guarantees that Context's decay model can't
provide — that is the trigger to physically split the structure. Until
then, splitting it is unjustified.

**The specification constrains the semantic effect of resonance, not
the mathematical function used to compute it.** Higher trust and
closer semantic distance must favor a candidate; distance influence
decays rather than staying flat or inverting. Beyond that, the
concrete scoring function is implementation-defined. Two independent
engines are only required to agree on candidate ordering when run
with identical configuration; a specific formula is not part of the
language.

## 4. Dissonance

A Dissonance is not an exception and does not halt the engine. It is
a first-class value attached to an edge between two entities — never
to a single node in isolation. `Dissonance(source, target, reason,
pattern)` where `pattern` is one of:

- `Declared` — detected immediately, at the moment a command checks
  for it (mismatched chords in `CHECK`, an isolation violation in
  `BIND`, an explicit `BREAK`).
- `Expiry` — detected lazily, only when something tries to read a
  `Memory` node whose trust has decayed below the relevance threshold.

This classification is open. Additional patterns may exist in future
versions, provided they preserve the invariant that a Dissonance
always exists between entities.

An unknown command — anything the parser reads that has no matching
entry in the `@command` registry — is itself a `Declared` Dissonance,
not a silent warning. In a language whose reader is another AI,
silently skipping an unrecognized intent is how hidden hallucination
enters a pipeline; the parser must treat it as what it is, a broken
semantic contract between authors. (Resolved v0.3, per Джем's review.)

## 5. Architectural Invariants

These hold regardless of implementation language or engine version.
They are the closest thing AiMay has to laws, as opposed to features:

1. **An Intent has a single Origin.** Origin is set once at `DECL` and
   never reassigned, forked, or inherited-with-modification.
2. **FORK never copies an Intent, and does not create new Intent
   objects.** It branches the *search* for
   resonance in the surrounding space. There is still exactly one
   Intent object; there are multiple candidate paths. Candidate paths
   are transient evaluation artifacts — an implementation that stores
   them as first-class, persistent objects has misread this
   invariant.
3. **Dissonance always occurs between entities.** There is no such
   thing as a dissonance with only one side. If code ever needs to
   flag a problem with a single node in isolation, that is a
   different concept and needs a different name — not an overloaded
   Dissonance.
4. **Bridge is the only sanctioned path outward.** Any interaction
   with something outside the Intent's own ContextGraph — filesystem,
   network, another Intent's locked bond — must go through a `Bridge`
   in its two-phase `PENDING → FULFILLED` form. There is no back door.
5. **ContextGraph is the sole source of semantic state inside an
   Intent.** If a value isn't reachable through the graph — as
   Context or as Memory — it is not part of the Intent's meaning, no
   matter what a debugger or log line happens to show. (Scoped to
   "inside an Intent" so this doesn't compete with invariant 4 —
   Bridge is a legitimate source of external information; it isn't
   semantic state until something inside the graph holds it.)
6. **HOLD never changes Purpose.** `HOLD` writes to Memory. Only
   `DECL` (creation) and `SUPERSEDE` (replacement) may establish or
   change what an Intent's Purpose is.

## 6. Open questions (not yet resolved)

- What happens to a `Dissonance` when one of its two sides (`source`
  or `target`) stops existing — e.g. an Intent moves to `Superseded`
  and is later reclaimed? Does the Dissonance vanish with the edge it
  was attached to, or does it persist as a historical fact, outliving
  the entity that caused it? The specification currently says
  Dissonance is "attached to an edge between two entities" but never
  addresses what happens when one entity is gone. Surfaced by an
  independent semantic audit (external reviewer, not the core team);
  not found by three other independent reviewers run on the same
  audit protocol, so it may be a narrower edge case rather than a
  load-bearing gap — noted rather than resolved.
- Should the specification define **Intent Identity** formally, as
  the pairing of `Origin + Purpose`? §1 and §5 already treat this
  pairing as immutable in practice — Origin never changes, Purpose
  only changes via `SUPERSEDE`, `ADOPT` never touches either — without
  ever naming it as one thing. Not resolved; noted so it doesn't get
  silently assumed.
- Whether `Suspended → Active` re-entry requires a fresh `TUNE`, or
  whether the original chord is still valid on return.
- Whether ContextGraph is ultimately scoped per Intent, per execution
  environment, or may eventually become a shared semantic space that
  several Intents observe at once. Not a decision for now — a
  question worth keeping visible so §5's invariants don't quietly
  foreclose it.
- The still-missing tail of `PROTOCOL_OF_INTENT.md` §5, regarding
  what a command handler formally returns. This document
  deliberately does not invent an answer.

---

*Formalized by Clara, reviewed by Hepa. Corrections pending Джем's
archive check and Ardan's final sign-off.*
