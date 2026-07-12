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
