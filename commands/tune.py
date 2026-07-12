from engine.colors import C
from .registry import command


@command("TUNE")
def cmd_tune(engine, args: list):
    """TUNE <target> <new_overtone>"""
    target   = args[0] if args else "self"
    overtone = args[1] if len(args) > 1 else "neutral"

    if target == "self" and engine.current:
        old = engine.current.chord[:]
        if overtone not in engine.current.chord:
            engine.current.chord.append(overtone)
        engine._log("TUNE", (
            f"self.chord: {C.MAGENTA}{old}{C.RESET} → "
            f"{C.MAGENTA}{engine.current.chord}{C.RESET}"
        ), C.MAGENTA)
    else:
        engine._log("TUNE", (
            f"{C.YELLOW}invite({overtone}){C.RESET} → "
            f"{target} (очікуємо згоди)"
        ), C.YELLOW)
