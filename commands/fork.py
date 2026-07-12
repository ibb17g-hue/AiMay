from engine.colors import C
from .registry import command


@command("FORK")
def cmd_fork(engine, args: list):
    """FORK <signal> ~> [A, B, C]"""
    targets_raw = " ".join(args)
    targets = [t.strip('[],"~> ') for t in targets_raw.split()
               if t.strip('[],"~> ') and t not in ("Resonance", "~>")]

    engine._log("FORK", (
        f"розгалуження → {C.YELLOW}{targets}{C.RESET} "
        f"(паралельно, ідентичність Intent збережена)"
    ), C.YELLOW)

    source_id = engine.current.name if engine.current else "self"
    if source_id not in engine.space.graph.nodes:
        engine.space.graph.add_node(source_id, kind="intent", trust=1.0)

    candidate_ids = engine.space.spawn_fork_targets(source_id, targets)

    # Реальний BFS-резонанс від Intent-вузла по щойно доданих гілках
    results = engine.space.resonance(source_id)
    # лишаємо тільки щойно породжені candidate-вузли цього FORK
    results = [(nid, score) for nid, score in results if nid in candidate_ids]
    engine.last_fork_results = results  # список (id, score), відсортований за спаданням

    for nid, score in results:
        short = nid.split(".")[-1]
        engine._log("FORK", (
            f"  {C.GRAY}↳{C.RESET} {C.CYAN}{short}{C.RESET} "
            f"resonance.score: {C.GREEN}{score}{C.RESET}"
        ), C.GRAY)
