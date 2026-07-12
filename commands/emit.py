from engine.colors import C
from .registry import command


@command("EMIT")
def cmd_emit(engine, args: list):
    """EMIT <target> <message>"""
    target  = args[0]
    message = " ".join(args[1:]).strip('"')

    engine._log("EMIT", (
        f"→ {C.YELLOW}{target}{C.RESET}: "
        f"{C.WHITE}\"{message}\"{C.RESET}"
    ), C.YELLOW)
