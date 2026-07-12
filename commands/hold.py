from datetime import datetime
from engine.colors import C
from .registry import command


@command("HOLD")
def cmd_hold(engine, args: list):
    """HOLD <key> [trust: N] [timestamp: ...]"""
    if not args:
        return

    key   = args[0]
    trust = 1.0
    for a in args:
        if a.startswith("trust:"):
            try:
                trust = float(a.split(":")[1])
            except ValueError:
                pass

    value = f"snapshot@{datetime.now().strftime('%H:%M:%S')}"
    if engine.current:
        engine.current.hold(key, value, trust)

    engine._log("HOLD", (
        f"{C.CYAN}{key}{C.RESET} "
        f"trust:{C.GREEN}{trust:.2f}{C.RESET}  "
        f"timestamp:{C.GRAY}{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}{C.RESET}  "
        f"{C.GRAY}(δ decay_rate={engine.current.context.nodes[key].decay_rate if engine.current else '?'}){C.RESET}"
    ), C.CYAN)
