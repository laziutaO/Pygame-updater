"""Dijkstra's algorithm. Optimal for non-uniform edge costs without a heuristic."""
import heapq

from .astar import reconstruct_path


def dijkstra(graph, start, end):
    """Returns list of nodes start..end inclusive (least-cost path), or None."""
    start, end = tuple(start), tuple(end)
    open_heap = [(0.0, 0, start)]
    came_from = {start: None}
    g_score = {start: 0.0}
    closed = set()
    counter = 0
    while open_heap:
        _, _, current = heapq.heappop(open_heap)
        if current in closed:
            continue
        closed.add(current)
        if current == end:
            return reconstruct_path(came_from, current)
        for n in graph.neighbors(current):
            if n in closed:
                continue
            tentative = g_score[current] + graph.cost(current, n)
            if n not in g_score or tentative < g_score[n]:
                g_score[n] = tentative
                came_from[n] = current
                counter += 1
                heapq.heappush(open_heap, (tentative, counter, n))
    return None


class Dijkstra:
    def __init__(self, graph):
        self.graph = graph

    def search(self, start, end):
        return dijkstra(self.graph, start, end)
