from engine.colors import C
from engine.dissonance import Dissonance
from .registry import command


@command("BIND")
def cmd_bind(engine, args: list):
    """BIND <a> <b>"""
    a = args[0] if args else "self"
    b = args[1] if len(args) > 1 else "incoming"

    if not engine.current:
        return

    any_bridge_open = any(br.is_open() for br in engine.bridges.values())

    if any_bridge_open and (engine.current.is_locked(a) or engine.current.is_locked(b)):
        ds = Dissonance(
            source=a, target=b,
            reason="isolation_violation: bridge is open, pair is locked",
            pattern=Dissonance.DECLARED,
        )
        engine.dissonances.append(ds)
        engine._log("BIND", (
            f"{C.RED}✗{C.RESET} {a} ↔ {b} — заблоковано, "
            f"{C.RED}{ds}{C.RESET}"
        ), C.RED)
        return

    engine.current.bind(a, b, locked=True)
    bond = f"{a} ↔ {b}"
    engine._log("BIND", (
        f"{C.GREEN}{bond}{C.RESET} "
        f"— зв'язок створено у графі (постійно)"
    ), C.GREEN)
