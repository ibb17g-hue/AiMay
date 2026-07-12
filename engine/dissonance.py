"""Dissonance — не помилка, а сигнал про незбіг. Належить ребру графа."""

from datetime import datetime


class Dissonance:
    DECLARED = "declared"   # виявлено одразу при перевірці (CHECK, BIND)
    EXPIRY   = "expiry"     # виявлено через згасання довіри (HOLD decay)

    def __init__(self, source: str, target: str, reason: str,
                 pattern: str = DECLARED, auto: bool = True):
        self.source    = source
        self.target    = target
        self.reason    = reason
        self.pattern   = pattern
        self.auto      = auto
        self.timestamp = datetime.now()

    def __str__(self):
        return (f"Dissonance[{self.pattern}]({self.source} <-> {self.target}: "
                f"{self.reason})")
