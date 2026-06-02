import heapq
import math


def euclidean(a: tuple, b: tuple) -> float:
    return math.hypot(a[0] - b[0], a[1] - b[1])


def manhattan(a: tuple, b: tuple) -> float:
    return abs(a[0] - b[0]) + abs(a[1] - b[1])


def reconstruct_path(came_from: dict, node: tuple) -> list:
    path = [node]
    while came_from.get(node) is not None:
        node = came_from[node]
        path.append(node)
    return path[::-1]


class GridGraph:
    """Generic 4-/8-connected grid graph.

    `passable_fn(cell)` returns True if the cell is walkable. `entity_size`
    extends the test to cover a footprint larger than one cell. `step` controls
    the spacing between neighbors.
    """
    DIAG = [(-1, -1), (0, -1), (1, -1),
            (-1,  0),          (1,  0),
            (-1,  1), (0,  1), (1,  1)]
    CARD = [(0, -1), (-1, 0), (1, 0), (0, 1)]

    def __init__(self, passable_fn, allow_diagonal=True, entity_size=(1, 1), step=1):
        self.passable_fn = passable_fn
        self.allow_diagonal = allow_diagonal
        self.entity_size = entity_size
        self.step = step
        self._offsets = self.DIAG if allow_diagonal else self.CARD

    def is_clear(self, cell):
        ew, eh = self.entity_size
        if not self.passable_fn(cell):
            return False
        if ew > 1 and not self.passable_fn((cell[0] + ew - 1, cell[1])):
            return False
        if eh > 1 and not self.passable_fn((cell[0], cell[1] + eh - 1)):
            return False
        if ew > 1 and eh > 1 and not self.passable_fn((cell[0] + ew - 1, cell[1] + eh - 1)):
            return False
        return True

    def neighbors(self, cell: tuple) :
        s = self.step
        for ox, oy in self._offsets:
            n = (cell[0] + ox * s, cell[1] + oy * s)
            if self.is_clear(n):
                yield n

    def cost(self, a: tuple, b: tuple):
        return math.sqrt(2) if a[0] != b[0] and a[1] != b[1] else 1.0


def astar(graph, start, end, heuristic=euclidean):
    """A* search. Returns list of nodes from start position to end or None."""
    start, end = tuple(start), tuple(end)
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
        for n in graph.neighbors(current):
            if n in closed:
                continue
            tentative = g_score[current] + graph.cost(current, n)
            if n not in g_score or tentative < g_score[n]:
                g_score[n] = tentative
                came_from[n] = current
                counter += 1
                heapq.heappush(open_heap, (tentative + heuristic(n, end), counter, n))
    return None


class AStar:
    def __init__(self, graph, heuristic=euclidean):
        self.graph = graph
        self.heuristic = heuristic
        self.path = []
        self.path_index = 0
        self.finished = False

    def search(self, start, end):
        return astar(self.graph, start, end, self.heuristic)

    def get_next_position(self, start, end):
        if self.path_index >= len(self.path):
            self.finished = False
            new_path = self.search(start, end)
            if new_path is None:
                self.finished = True
                self.path = []
                return start
            self.path = new_path
            self.path_index = 0
        self.path_index += 1
        return self.path[self.path_index - 1]


