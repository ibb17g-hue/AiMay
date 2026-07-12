"""
ContextNode / ContextGraph
==========================
Протокол намірів, розділ 1: заміна лінійного dict у пам'яті на мережу
вузлів. Кожен ContextNode — сутність, намір або стан. Резонанс між
вузлами шукається обходом у ширину (BFS), а вага (score) — функція
від дистанції в графі та поточної довіри вузла:

    score = trust(node) * exp(-alpha * distance)

Довіра сама згасає з часом (розділ 2 протоколу) — тому й score
"старіє", навіть якщо граф не змінюється.
"""

import math
import time
from collections import deque


class ContextNode:
    """Один вузол семантичного графу з власним затуханням довіри."""

    DECAY_RATE = 0.05

    def __init__(self, node_id: str, kind: str = "entity",
                 data=None, trust: float = 1.0, decay_rate: float = None):
        self.id         = node_id
        self.kind       = kind
        self.data       = data
        self.trust0     = trust
        self.decay_rate = decay_rate if decay_rate is not None else self.DECAY_RATE
        self.created_at = time.time()
        self.edges: dict[str, float] = {}   # neighbor_id -> distance

    def current_trust(self) -> float:
        age = time.time() - self.created_at
        decayed = self.trust0 * math.exp(-self.decay_rate * age)
        return round(max(0.0, decayed), 4)

    def is_relevant(self, threshold: float = 0.2) -> bool:
        return self.current_trust() >= threshold


class ContextGraph:
    """Семантична пам'ять Intent — граф ContextNode замість dict."""

    def __init__(self):
        self.nodes: dict[str, ContextNode] = {}

    def add_node(self, node_id: str, kind: str = "entity",
                 data=None, trust: float = 1.0) -> ContextNode:
        node = ContextNode(node_id, kind, data, trust)
        self.nodes[node_id] = node
        return node

    def add_edge(self, a_id: str, b_id: str,
                 distance: float = 1.0, bidirectional: bool = True):
        if a_id not in self.nodes:
            self.add_node(a_id)
        if b_id not in self.nodes:
            self.add_node(b_id)
        self.nodes[a_id].edges[b_id] = distance
        if bidirectional:
            self.nodes[b_id].edges[a_id] = distance

    def bfs_resonance(self, start_id: str, alpha: float = 0.3):
        """
        BFS від start_id. distance — сума ваг ребер найкоротшого шляху.
        Повертає [(node_id, score), ...] за спаданням score.
        """
        if start_id not in self.nodes:
            return []

        visited = {start_id: 0.0}
        queue = deque([start_id])
        while queue:
            cur = queue.popleft()
            cur_dist = visited[cur]
            for neigh, w in self.nodes[cur].edges.items():
                nd = cur_dist + w
                if neigh not in visited or nd < visited[neigh]:
                    visited[neigh] = nd
                    queue.append(neigh)

        results = []
        for node_id, distance in visited.items():
            if node_id == start_id:
                continue
            node = self.nodes[node_id]
            score = round(node.current_trust() * math.exp(-alpha * distance), 4)
            results.append((node_id, score))

        results.sort(key=lambda x: x[1], reverse=True)
        return results
