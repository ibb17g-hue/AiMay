"""Плагінна архітектура команд AiMay: кожен модуль реєструє себе через @command."""

from .registry import COMMAND_REGISTRY, command
from . import decl, emit, await_, check, tune, bind, hold, break_, fork, seal, bridge_cmd, task, adopt, query

__all__ = ["COMMAND_REGISTRY", "command"]
