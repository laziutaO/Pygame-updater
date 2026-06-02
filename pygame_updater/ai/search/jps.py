import heapq
import math
from .astar import GridGraph, euclidean, reconstruct_path


def jps(graph: GridGraph, start: tuple, end: tuple, heuristic=euclidean):
    """Returns list of jump points, or None."""
    start, end = tuple(start), tuple(end)
    if not graph.is_clear(start) or not graph.is_clear(end):
        return None
    s = graph.step

    def clear(p):
        return graph.is_clear(p)

    def jump(node, dx, dy):
        nx, ny = node[0] + dx * s, node[1] + dy * s
        n = (nx, ny)
        if not clear(n):
            return None
        if n == end:
            return n
        if dx != 0 and dy != 0:
            if clear((nx - dx * s, ny + dy * s)) and not clear((nx - dx * s, ny)):
                return n
            if clear((nx + dx * s, ny - dy * s)) and not clear((nx, ny - dy * s)):
                return n
            if jump(n, dx, 0) is not None or jump(n, 0, dy) is not None:
                return n
        elif dx != 0:
            if clear((nx + dx * s, ny + s)) and not clear((nx, ny + s)):
                return n
            if clear((nx + dx * s, ny - s)) and not clear((nx, ny - s)):
                return n
        else:
            if clear((nx + s, ny + dy * s)) and not clear((nx + s, ny)):
                return n
            if clear((nx - s, ny + dy * s)) and not clear((nx - s, ny)):
                return n
        return jump(n, dx, dy)

    directions = [(-1, -1), (0, -1), (1, -1),
                  (-1,  0),          (1,  0),
                  (-1,  1), (0,  1), (1,  1)]

    open_heap = [(heuristic(start, end), 0, start)]
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
        for dx, dy in directions:
            jp = jump(current, dx, dy)
            if jp is None:
                continue
            tentative = g_score[current] + math.hypot(jp[0] - current[0], jp[1] - current[1])
            if jp not in g_score or tentative < g_score[jp]:
                g_score[jp] = tentative
                came_from[jp] = current
                counter += 1
                heapq.heappush(open_heap, (tentative + heuristic(jp, end), counter, jp))
    return None


class JPS:
    def __init__(self, graph: GridGraph):
        self.graph = graph

    def search(self, start: tuple, end: tuple):
        return jps(self.graph, start, end)
