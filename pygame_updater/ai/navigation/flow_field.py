import heapq
import math
from typing import Protocol


class FlowField:
    def __init__(self, graph):
        self.graph = graph
        self.cost = {}
        self.flow = {}

    def build(self, target):
        """Compute cost and unit-direction fields with `target` as the goal."""
        target = tuple(target)
        self.cost = {target: 0.0}
        self.flow = {}
        heap = [(0.0, 0, target)]
        counter = 0
        while heap:
            c, _, current = heapq.heappop(heap)
            if c > self.cost.get(current, float('inf')):
                continue
            for n in self.graph.neighbors(current):
                new_c = c + self.graph.cost(current, n)
                if new_c < self.cost.get(n, float('inf')):
                    self.cost[n] = new_c
                    counter += 1
                    heapq.heappush(heap, (new_c, counter, n))
        for cell, c in self.cost.items():
            best = None
            best_cost = c
            for n in self.graph.neighbors(cell):
                nc = self.cost.get(n, float('inf'))
                if nc < best_cost:
                    best_cost = nc
                    best = n
            if best is None:
                self.flow[cell] = (0.0, 0.0)
            else:
                dx, dy = best[0] - cell[0], best[1] - cell[1]
                d = math.hypot(dx, dy)
                self.flow[cell] = (dx / d, dy / d) if d > 0 else (0.0, 0.0)

    def direction(self, cell):
        return self.flow.get(tuple(cell), (0.0, 0.0))
