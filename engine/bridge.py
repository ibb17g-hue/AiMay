"""Bridge — єдиний портал між Intent-графом і зовнішнім світом.

Двофазний: BRIDGE відкриває канал у стані PENDING, SEAL закриває його
в FULFILLED (або BREAK переводить у BROKEN при дисонансі). Рушій не
має права завершити роботу, поки лишаються незакриті (PENDING) мости.
"""


class Bridge:
    PENDING   = "pending"
    FULFILLED = "fulfilled"
    BROKEN    = "broken"

    def __init__(self, name: str, origin: str = "Human",
                 capabilities: list = None, scope: str = "*"):
        self.name         = name
        self.origin       = origin
        self.capabilities = capabilities or ["read"]
        self.scope        = scope
        self.state        = self.PENDING

    def can(self, action: str) -> bool:
        return action in self.capabilities

    def execute(self, action: str, payload: str) -> str:
        if not self.can(action):
            return f"[BRIDGE DENIED] {self.name} не має capability '{action}'"
        return f"[BRIDGE:{self.name}] {action}({payload!r}) → виконано"

    def seal(self):
        self.state = self.FULFILLED

    def break_(self):
        self.state = self.BROKEN

    def is_open(self) -> bool:
        return self.state == self.PENDING
