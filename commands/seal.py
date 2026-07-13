from engine.colors import C
from .registry import command


@command("SEAL")
def cmd_seal(engine, args: list):
    """SEAL <intent_name>"""
    name = args[0] if args else (engine.current.name if engine.current else "?")

    intent = engine.intents.get(name) or engine.current
    if intent:
        unresolved = intent.has_unresolved_children(engine.intents)
        if unresolved:
            engine._log("SEAL", (
                f"{C.RED}✗{C.RESET} {C.CYAN}{name}{C.RESET} → "
                f"НЕ fulfilled — очікує TASK: {C.YELLOW}{unresolved}{C.RESET}"
            ), C.RED)
            return

        intent.seal()
        bonds_info = (f"  bonds:{C.GREEN}{[f'{a}↔{b}' for a, b, _ in intent.bonds]}{C.RESET}"
                      if intent.bonds else "")
        mem_keys = list(intent.context.nodes.keys())
        mem_info = f"  memory:{C.CYAN}{mem_keys}{C.RESET}" if mem_keys else ""
        engine._log("SEAL", (
            f"{C.CYAN}{name}{C.RESET} → {C.GREEN}fulfilled ✓{C.RESET}"
            f"{bonds_info}{mem_info}"
        ), C.GREEN)
    else:
        engine._log("SEAL", f"{C.YELLOW}{name}{C.RESET} → fulfilled", C.GREEN)

    # Закриваємо будь-які мости, відкриті саме цим Intent, якщо такі лишились PENDING
    for bridge in engine.bridges.values():
        if bridge.is_open():
            bridge.seal()
            engine._log("SEAL", (
                f"  {C.GRAY}↳ bridge {bridge.name}: pending → fulfilled{C.RESET}"
            ), C.GRAY)

    engine.current = None
