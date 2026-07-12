"""
AiMaySpaceSimulator
====================
У v0.1 "простір" був фікцією: incoming.chord завжди дорівнював ["open"],
FORK видавав score від голого hash() рядка. У v0.2 симулятор тримає
власний ContextGraph, який живе між викликами команд у межах одного
запуску рушія — DECL, FORK і AWAIT читають і пишуть в один і той самий
граф, а не породжують ізольовані випадкові числа щоразу.
"""

import random
from .context_node import ContextGraph


class AiMaySpaceSimulator:
    def __init__(self, seed: int = None):
        self.graph = ContextGraph()
        self._rng  = random.Random(seed)
        self.graph.add_node("Space", kind="root", trust=1.0)

    def populate_incoming(self, intent_name: str, chord: list) -> str:
        """DECL: простір породжує вхідний Intent-вузол із власним chord."""
        incoming_id = f"incoming.{intent_name}"
        # incoming резонує з нашим chord, якщо хоч раз перетинається "open"
        inc_chord = chord if chord else ["open"]
        self.graph.add_node(incoming_id, kind="incoming_intent",
                             data={"chord": inc_chord}, trust=1.0)
        self.graph.add_edge("Space", incoming_id, distance=1.0)
        return incoming_id

    def spawn_fork_targets(self, source_id: str, targets: list) -> list:
        """FORK: породжує candidate-вузли з живою (не хардкодною) trust/distance."""
        ids = []
        for t in targets:
            node_id = f"{source_id}.{t}"
            trust    = round(0.65 + self._rng.random() * 0.35, 2)
            distance = round(0.2 + self._rng.random() * 1.6, 2)
            self.graph.add_node(node_id, kind="candidate", trust=trust)
            self.graph.add_edge(source_id, node_id, distance=distance)
            ids.append(node_id)
        return ids

    def resonance(self, from_id: str, alpha: float = 0.3):
        """Обгортка над BFS-резонансом графа простору."""
        return self.graph.bfs_resonance(from_id, alpha=alpha)
