from engine.colors import C
from engine.dissonance import Dissonance
from .registry import command


@command("CHECK")
def cmd_check(engine, args: list):
    """CHECK <expr>"""
    expr = " ".join(args)

    if not engine.current:
        engine._log("CHECK", f"{C.RED}✗ немає активного Intent{C.RESET}", C.RED)
        return

    # ── best_match: результат FORK через BFS-резонанс, не хардкод ──────
    if "best_match" in expr:
        if engine.last_fork_results:
            best_id, best_score = engine.last_fork_results[0]  # вже відсортовано за score
            engine._log("CHECK", (
                f"{C.YELLOW}{expr}{C.RESET} → "
                f"best_match = {best_id} (resonance.score: {best_score})"
            ), C.GREEN)
            engine.current.hold("best_match", best_id, trust=best_score)
        else:
            engine._log("CHECK", (
                f"{C.RED}✗{C.RESET} {expr} → немає результатів FORK для порівняння"
            ), C.RED)
        return

    # ── chord-сумісність: звіряємо з реальним incoming-вузлом простору ──
    own_chord = engine.current.chord
    incoming_id = f"incoming.{engine.current.name}"
    inc_node = engine.space.graph.nodes.get(incoming_id)
    inc_chord = (inc_node.data.get("chord", ["open"]) if inc_node and inc_node.data
                 else ["open"])

    compatible = bool(set(own_chord) & set(inc_chord)) or \
                 "open" in own_chord or "open" in inc_chord

    if compatible:
        engine._log("CHECK", (
            f"{C.GREEN}✓{C.RESET} "
            f"self.chord{C.MAGENTA}{own_chord}{C.RESET} ~> "
            f"incoming.chord{C.MAGENTA}{inc_chord}{C.RESET} "
            f"— резонанс сумісний"
        ), C.GREEN)
    else:
        ds = Dissonance(
            source=engine.current.name,
            target="incoming",
            reason=f"overtone_mismatch({own_chord} vs {inc_chord})",
            pattern=Dissonance.DECLARED,
        )
        engine.dissonances.append(ds)
        engine._log("CHECK", (
            f"{C.RED}✗{C.RESET} {ds} → Dissonance згенеровано"
        ), C.RED)
