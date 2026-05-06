"""Breadth-first search. Optimal when all edges have the same cost."""
from collections import deque

from .astar import reconstruct_path


def bfs(graph, start, end):
    """Returns list of nodes start..end inclusive (uniform-cost shortest path), or None."""
    start, end = tuple(start), tuple(end)
    if start == end:
        return [start]
    came_from = {start: None}
    queue = deque([start])
    while queue:
        current = queue.popleft()
        for n in graph.neighbors(current):
            if n in came_from:
                continue
            came_from[n] = current
            if n == end:
                return reconstruct_path(came_from, n)
            queue.append(n)
    return None


class BFS:
    def __init__(self, graph):
        self.graph = graph

    def search(self, start, end):
        return bfs(self.graph, start, end)
