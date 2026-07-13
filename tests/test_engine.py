"""
Базові тести AiMay Engine v0.2.
Запуск: python -m pytest tests/ -v   (з кореня репозиторію)
або:    python tests/test_engine.py  (без pytest, ручні asserts)
"""

import os
import sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from engine.core import AiMayEngine
import commands


def test_all_ten_commands_registered():
    expected = {"DECL", "EMIT", "AWAIT", "CHECK", "TUNE",
                "BIND", "HOLD", "BREAK", "FORK", "SEAL", "BRIDGE"}
    registered = set(commands.COMMAND_REGISTRY.keys())
    missing = expected - registered
    assert not missing, f"Не зареєстровано: {missing}"


def test_fork_check_uses_real_resonance_not_hardcode():
    """Регресія на баг v0.1: CHECK best_match мав завжди повертати 'A, 0.94'."""
    engine = AiMayEngine(seed=1)
    engine.run_source("""
DECL Explorer "test" [open]
FORK Resonance ~> [A, B, C]
CHECK best_match <- max(resonance.score)
""")
    assert engine.last_fork_results, "FORK не наповнив last_fork_results"
    best_id, best_score = engine.last_fork_results[0]
    held = engine.intents["Explorer"].context.nodes.get("best_match")
    assert held is not None, "CHECK не записав best_match у пам'ять Intent"
    assert held.data == best_id, "CHECK записав не той candidate, що дійсно найкращий"


def test_await_bracket_list_parsed_correctly():
    """Регресія на баг v0.1: AWAIT [A, B, C] timeout: X ламав парсинг."""
    from commands.await_ import cmd_await

    engine = AiMayEngine(seed=1)
    engine.run_source('DECL X "test" [open]')
    # не має кидати виняток і не має "з'їдати" timeout у сигнал
    cmd_await(engine, "[ A , B , C ]  timeout: context.limit".split())


def test_bridge_two_phase():
    engine = AiMayEngine(seed=1)
    engine.run_source("""
BRIDGE FS origin: Human capabilities: [read] scope: local
DECL Reader "test" [focused]
SEAL Reader
""")
    assert engine.bridges["FS"].is_open() is False, "SEAL мав закрити відкритий Bridge"


def test_dissonance_on_chord_mismatch():
    engine = AiMayEngine(seed=1)
    engine.run_source("""
DECL Strict "test" [locked]
CHECK self.chord ~> incoming.chord
""")
    # incoming за замовчуванням отримує chord == власному DECL chord ([locked]),
    # тож щоб отримати dissonance, симулюємо конфлікт вручну:
    engine2 = AiMayEngine(seed=1)
    engine2.run_source('DECL Strict "test" [locked]')
    engine2.space.graph.nodes["incoming.Strict"].data = {"chord": ["different"]}
    engine2.run_source("CHECK self.chord ~> incoming.chord")
    assert len(engine2.dissonances) == 1
    assert engine2.dissonances[0].pattern == "declared"


def test_task_gates_parent_seal():
    """Decision №18: батько не fulfilled поки TASK-діти не resolved."""
    engine = AiMayEngine(seed=1)
    engine.run_source("""
DECL Explorer "test" [open]
TASK Scout "test child" [focused]
SEAL Explorer
""")
    assert engine.intents["Explorer"].status != "fulfilled", \
        "SEAL не мав пропустити батька з нерозв'язаним TASK"
    assert engine.intents["Scout"].spawned_by == "Explorer"
    assert engine.intents["Scout"].origin == engine.intents["Explorer"].origin

    engine.run_source("SEAL Scout\nSEAL Explorer")
    assert engine.intents["Explorer"].status == "fulfilled", \
        "SEAL мав пропустити батька після того, як TASK resolved"


def test_task_gating_blocks_only_seal_not_other_activity():
    """
    Гепа: gating не повинен блокувати всю активність Intent — лише
    перехід у fulfilled. EMIT/CHECK/BIND/HOLD мають працювати як
    завжди, поки TASK-дитина ще не resolved.
    """
    engine = AiMayEngine(seed=1)
    engine.run_source("""
DECL Explorer "test" [open]
TASK Scout "child" [focused]
EMIT Space "still working"
CHECK self.chord ~> incoming.chord
BIND self incoming.origin
HOLD Context.note trust: 1.0
""")
    explorer = engine.intents["Explorer"]
    assert explorer.status == "active", \
        "TASK gating не повинен сам собою міняти статус на щось інше"
    assert not engine.dissonances, \
        "EMIT/CHECK/BIND/HOLD не мають породжувати dissonance через незавершений TASK"
    assert ("self", "incoming.origin", True) in explorer.bonds, \
        "BIND мав спрацювати попри незавершений TASK"
    assert "Context.note" in explorer.context.nodes, \
        "HOLD мав спрацювати попри незавершений TASK"


def test_adopt_preserves_identity_through_generations():
    """
    Гепа: ADOPT never changes identity, only responsibility.
    A creates X (TASK) -> B adopts X -> X creates Y (TASK).
    origin(X) == origin(Y) == origin(A) незалежно від ADOPT;
    spawned_by(X) == B; spawned_by(Y) == X.
    """
    engine = AiMayEngine(seed=1)
    engine.run_source("""
DECL A "root A" [open]
TASK X "child of A" [open]
BIND self incoming.origin
""")
    x = engine.intents["X"]
    origin_before  = x.origin
    purpose_before = x.purpose

    engine.run_source('DECL B "root B" [open]')
    engine.run_source("ADOPT X")

    assert x.spawned_by == "B", "ADOPT мав перевести кураторство на B"
    assert x.origin == origin_before == engine.intents["A"].origin, \
        "ADOPT не повинен чіпати origin"
    assert x.purpose == purpose_before, "ADOPT не повинен чіпати purpose"

    # X створює Y через TASK — фокус вручну, бо окремої команди
    # "перемкнути активний Intent" поки немає
    engine.current = x
    engine.run_source('TASK Y "grandchild" [open]')

    y = engine.intents["Y"]
    assert y.origin == engine.intents["A"].origin, \
        "origin має передаватись крізь покоління незмінним"
    assert y.spawned_by == "X"
    assert x.spawned_by == "B", \
        "TASK від X не повинен був відкотити ADOPT над самим X"


def _engine_snapshot(engine):
    """Знімок усього стану, релевантного семантиці — для QUERY-тесту."""
    def node_snap(n):
        return (n.id, n.kind, n.data, n.trust0, n.decay_rate,
                n.created_at, tuple(sorted(n.edges.items())))

    intents_snap = {}
    for name, intent in engine.intents.items():
        intents_snap[name] = (
            intent.status, intent.origin, intent.purpose, intent.spawned_by,
            tuple(intent.bonds), tuple(intent.children),
            tuple(sorted((nid, node_snap(n)) for nid, n in intent.context.nodes.items())),
        )

    space_snap = tuple(sorted(
        (nid, node_snap(n)) for nid, n in engine.space.graph.nodes.items()
    ))
    bridges_snap = tuple(sorted(
        (name, b.state, tuple(b.capabilities), b.scope)
        for name, b in engine.bridges.items()
    ))
    return (intents_snap, space_snap, bridges_snap, len(engine.dissonances))


def test_query_is_purely_functional_no_side_effects():
    """
    Гепа: QUERY must be equivalent to a database read. ContextGraph,
    Memory, Trust, Resonance, Intent status, Bridges — byte-identical
    before and after any number of QUERY calls.
    """
    engine = AiMayEngine(seed=1)
    engine.run_source("""
DECL Explorer "test resonance" [open]
FORK Resonance ~> [A, B, C]
BRIDGE FS origin: Human capabilities: [read] scope: local
""")

    before = _engine_snapshot(engine)

    engine.run_source("""
QUERY Explorer memory
QUERY Explorer bonds
QUERY Explorer resonance
QUERY Explorer memory 0.5
QUERY NoSuchIntent memory
""")

    after = _engine_snapshot(engine)
    assert before == after, "QUERY змінив стан рушія — не має бути жодних побічних ефектів"


if __name__ == "__main__":
    tests = [v for k, v in list(globals().items()) if k.startswith("test_")]
    passed, failed = 0, 0
    for t in tests:
        try:
            t()
            print(f"  OK   {t.__name__}")
            passed += 1
        except AssertionError as e:
            print(f"  FAIL {t.__name__}: {e}")
            failed += 1
    print(f"\n{passed} passed, {failed} failed")
    sys.exit(1 if failed else 0)
