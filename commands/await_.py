import time
from engine.colors import C
from .registry import command


@command("AWAIT")
def cmd_await(engine, args: list):
    """AWAIT <signal | [A, B, C]> [timeout: ...]"""
    joined = " ".join(args)

    if joined.startswith("["):
        end = joined.index("]") + 1
        signal_raw = joined[:end]
        rest = joined[end:].strip()
        signal = [t.strip() for t in signal_raw.strip("[]").split(",") if t.strip()]
    else:
        signal = args[0] if args else "Resonance"
        rest = " ".join(args[1:]).strip()

    timeout = (f"  {C.GRAY}(timeout: {rest.split('timeout:')[1].strip()}){C.RESET}"
               if "timeout:" in rest else "")

    engine._log("AWAIT", (
        f"очікую {C.CYAN}{signal}{C.RESET}{timeout}..."
    ), C.CYAN)
    time.sleep(0.1)

    # Реальний запит до простору: чи є вузол incoming.<Intent> з релевантним резонансом
    incoming_id = f"incoming.{engine.current.name}" if engine.current else None
    if incoming_id and incoming_id in engine.space.graph.nodes:
        engine._log("AWAIT", (
            f"{C.GREEN}✓{C.RESET} Resonance отримано від "
            f"{C.CYAN}{incoming_id}{C.RESET}"
        ), C.GREEN)
    else:
        engine._log("AWAIT", (
            f"{C.YELLOW}…{C.RESET} сигнал {signal} без відповіді простору "
            f"(немає активного Intent для звірки)"
        ), C.YELLOW)
