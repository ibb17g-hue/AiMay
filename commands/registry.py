"""
Реєстр команд AiMay.
====================
Диспетчер у engine/core.py не містить хардкод cmd_DECL/cmd_EMIT/... —
натомість кожен файл у commands/ реєструє себе декоратором @command(name)
при імпорті. core.py лише викликає commands.load_all() і бере обробник
з COMMAND_REGISTRY.
"""

COMMAND_REGISTRY: dict[str, callable] = {}


def command(name: str):
    """Декоратор реєстрації: @command("HOLD") над def cmd_hold(engine, args)."""
    def deco(fn):
        COMMAND_REGISTRY[name.upper()] = fn
        return fn
    return deco
