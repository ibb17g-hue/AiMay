from engine.colors import C
from .registry import command


@command("QUERY")
def cmd_query(engine, args: list):
    """QUERY <IntentName> <bonds|memory|resonance> [threshold]

    Read-only. QUERY never mutates ContextGraph, Memory, Trust,
    Resonance, Intent status, or Bridges — equivalent to a database
    read, not an action. No hidden caches, no "last accessed" writes.
    """
    if not args:
        engine._log("QUERY", f"{C.RED}✗ бракує аргументів{C.RESET}", C.RED)
        return

    target_name = args[0]
    mode = args[1].lower() if len(args) > 1 else "memory"
    target = engine.intents.get(target_name)
    if not target:
        engine._log("QUERY", (
            f"{C.RED}✗ невідомий Intent: {target_name}{C.RESET}"
        ), C.RED)
        return

    if mode == "bonds":
        result = [f"{a}↔{b}" for a, b, _locked in target.bonds]
        engine._log("QUERY", (
            f"{C.CYAN}{target_name}.bonds{C.RESET} → {C.MAGENTA}{result}{C.RESET}"
        ), C.CYAN)

    elif mode == "memory":
        threshold = float(args[2]) if len(args) > 2 else 0.0
        # .current_trust() — чиста функція від часу, нічого не пише в вузол
        result = [(nid, node.current_trust())
                  for nid, node in target.context.nodes.items()
                  if node.current_trust() >= threshold]
        engine._log("QUERY", (
            f"{C.CYAN}{target_name}.memory{C.RESET}(trust≥{threshold}) → "
            f"{C.MAGENTA}{result}{C.RESET}"
        ), C.CYAN)

    elif mode == "resonance":
        if target_name in engine.space.graph.nodes:
            results = engine.space.resonance(target_name)  # чистий BFS, не пише в граф
        else:
            results = []
        engine._log("QUERY", (
            f"{C.CYAN}{target_name}.resonance{C.RESET} → "
            f"{C.MAGENTA}{results[:5]}{C.RESET}"
        ), C.CYAN)

    else:
        engine._log("QUERY", (
            f"{C.RED}✗ невідомий режим QUERY: {mode} "
            f"(bonds | memory | resonance){C.RESET}"
        ), C.RED)
