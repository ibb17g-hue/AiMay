from engine.colors import C
from engine.intent import Intent
from .registry import command


@command("DECL")
def cmd_decl(engine, args: list):
    """DECL <name> <purpose> [chord...]"""
    name    = args[0]
    purpose = args[1].strip('"')
    chord   = [c.strip('[],"') for c in args[2:] if c.strip('[],"')]

    intent = Intent(name, purpose, chord)
    engine.intents[name] = intent
    engine.current = intent
    engine.space.populate_incoming(name, chord)  # простір реагує на новий Intent

    engine._log("DECL", (
        f"{C.CYAN}{name}{C.RESET} — {purpose} "
        f"{C.MAGENTA}{chord}{C.RESET}"
    ), C.CYAN)
