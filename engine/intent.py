"""Intent — базова одиниця AiMay. Пам'ять тепер ContextGraph, не dict."""

from datetime import datetime
from .context_node import ContextGraph


class Intent:
    ACTIVE     = "active"
    FULFILLED  = "fulfilled"
    SUSPENDED  = "suspended"
    SUPERSEDED = "superseded"

    def __init__(self, name: str, purpose: str, chord: list,
                 origin: str = "Human", spawned_by: str = "Human"):
        self.name        = name
        self.purpose     = purpose
        self.chord       = chord
        self.origin      = origin       # незмінний — завжди людина-першоджерело
        self.spawned_by  = spawned_by   # безпосередній батько
        self.status      = self.ACTIVE
        self.context     = ContextGraph()   # семантична пам'ять — граф
        self.bonds: list[tuple[str, str, bool]] = []   # (a, b, locked)
        self._locked_nodes: set[str] = set()
        self.created_at  = datetime.now()

    # ── Пам'ять ──────────────────────────────────────────────────────────

    def hold(self, key: str, value, trust: float = 1.0):
        self.context.add_node(key, kind="memory", data=value, trust=trust)

    def get(self, key: str, threshold: float = 0.2):
        """Повертає (node, dissonance_reason_or_None)."""
        node = self.context.nodes.get(key)
        if node is None:
            return None, None
        if not node.is_relevant(threshold):
            return node, f"trust decayed below {threshold} for '{key}'"
        return node, None

    # ── Bonds / ізоляція (розділ 1, "Обмеження ізоляції") ───────────────

    def bind(self, a: str, b: str, locked: bool = True):
        self.bonds.append((a, b, locked))
        if locked:
            self._locked_nodes.add(a)
            self._locked_nodes.add(b)

    def unlock(self, node_id: str):
        self._locked_nodes.discard(node_id)

    def is_locked(self, node_id: str) -> bool:
        return node_id in self._locked_nodes

    # ── Стани ────────────────────────────────────────────────────────────

    def seal(self, reason: str = "metric fulfilled"):
        self.status = self.FULFILLED
        return reason

    def suspend(self, reason: str = "awaiting conditions"):
        self.status = self.SUSPENDED
        return reason

    def supersede(self, by: str):
        self.status = self.SUPERSEDED
        return f"superseded by {by}"
