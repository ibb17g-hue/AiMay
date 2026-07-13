from engine.colors import C
from .registry import command


@command("ADOPT")
def cmd_adopt(engine, args: list):
    """ADOPT <target>

    Invariant (Гепа, Decision №18/19): ADOPT never changes identity.
    It changes only responsibility. Після ADOPT незмінні: origin,
    purpose, context, memory, bonds, історія Intent. Змінюється лише
    spawned_by — хто тепер відповідає за подальшу долю Intent.
    Це не BIND (BIND — відношення зв'язку) і не переписування історії.
    """
    if not engine.current:
        engine._log("ADOPT", f"{C.RED}✗ немає активного Intent-куратора{C.RESET}", C.RED)
        return

    target_name = args[0] if args else None
    target = engine.intents.get(target_name) if target_name else None
    if not target:
        engine._log("ADOPT", (
            f"{C.RED}✗ невідомий Intent для ADOPT: {target_name}{C.RESET}"
        ), C.RED)
        return

    old_curator = target.spawned_by
    target.spawned_by = engine.current.name   # єдине поле, що змінюється

    engine._log("ADOPT", (
        f"{C.CYAN}{engine.current.name}{C.RESET} приймає кураторство над "
        f"{C.CYAN}{target_name}{C.RESET}  "
        f"spawned_by: {C.GRAY}{old_curator}{C.RESET} → {C.GREEN}{engine.current.name}{C.RESET}  "
        f"{C.GRAY}(origin незмінний: {target.origin}){C.RESET}"
    ), C.GREEN)
