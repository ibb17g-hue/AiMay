from engine.colors import C
from engine.intent import Intent
from .registry import command


@command("TASK")
def cmd_task(engine, args: list):
    """TASK <ChildName> <"purpose"> [chord]

    Породжує дочірній Intent: власний Purpose, успадкований Origin
    батька, spawned_by = батько. Батьківський Intent не може бути
    fulfilled (SEAL), поки лишаються нерозв'язані TASK-діти —
    Decision №18.
    """
    if not engine.current:
        engine._log("TASK", f"{C.RED}✗ немає активного батьківського Intent{C.RESET}", C.RED)
        return

    name    = args[0]
    purpose = args[1].strip('"') if len(args) > 1 else "unnamed task"
    chord   = [c.strip('[],"') for c in args[2:] if c.strip('[],"')]

    parent = engine.current
    child = Intent(name, purpose, chord,
                    origin=parent.origin,       # успадковано, не переписується
                    spawned_by=parent.name)      # відповідальність, не BIND
    engine.intents[name] = child
    parent.children.append(name)
    engine.space.populate_incoming(name, chord)

    engine._log("TASK", (
        f"{C.CYAN}{name}{C.RESET} ⊂ {C.CYAN}{parent.name}{C.RESET}  "
        f"purpose:\"{purpose}\"  chord:{C.MAGENTA}{chord}{C.RESET}  "
        f"origin:{C.GRAY}{child.origin}{C.RESET} (успадковано)"
    ), C.CYAN)
