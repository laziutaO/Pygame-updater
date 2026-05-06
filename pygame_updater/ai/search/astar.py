"""A* and the shared `GridGraph` abstraction used by every search algorithm in this package.

Algorithm functions take a `graph` exposing:
    - neighbors(node)   -> iterable of reachable neighbor nodes
    - cost(a, b)        -> step cost between adjacent nodes
And return a list of nodes from start to end (inclusive) or None if no path.
"""
import heapq
import math


def euclidean(a, b):
    return math.hypot(a[0] - b[0], a[1] - b[1])


def manhattan(a, b):
    return abs(a[0] - b[0]) + abs(a[1] - b[1])


def reconstruct_path(came_from, node):
    """Walk a came_from chain (root maps to None) back to the start."""
    path = [node]
    while came_from.get(node) is not None:
        node = came_from[node]
        path.append(node)
    return path[::-1]


class GridGraph:
    """Generic 4-/8-connected grid graph.

    `passable_fn(cell)` returns True if the cell is walkable. `entity_size`
    extends the test to cover a footprint larger than one cell. `step` controls
    the spacing between neighbors (1 = adjacent cells; raise it for pixel-grids
    where 1-pixel resolution is too fine).
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

    def neighbors(self, cell):
        s = self.step
        for ox, oy in self._offsets:
            n = (cell[0] + ox * s, cell[1] + oy * s)
            if self.is_clear(n):
                yield n

    def cost(self, a, b):
        return math.sqrt(2) if a[0] != b[0] and a[1] != b[1] else 1.0


def astar(graph, start, end, heuristic=euclidean):
    """A* search. Returns list of nodes start..end inclusive, or None."""
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
    """Stateful path-follower wrapping `astar()`."""
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


class SearchAction:
    """Legacy pixel-resolution A* over a tilemap. Preserved for existing callers.

    `entity_width` / `entity_height` are in pixels; neighbors step ±1 pixel and
    the 4 corners of the entity rect are checked against `tilemap.is_occupied_tile`.
    For new code, prefer `AStar(GridGraph(...))`.
    """
    def __init__(self, entity_width, entity_height, tilemap=None):
        self.path = []
        self.path_index = 0
        self.finished = False
        self.tilemap = tilemap
        self.entity_width = entity_width
        self.entity_height = entity_height

    def __neighbors(self, current):
        out = []
        for x in range(-1, 2):
            for y in range(-1, 2):
                if x == 0 and y == 0:
                    continue
                neighbor = (current[0] + x, current[1] + y)
                bl = (neighbor[0], neighbor[1] + self.entity_height)
                tr = (neighbor[0] + self.entity_width, neighbor[1])
                br = (tr[0], bl[1])
                if self.tilemap is None or (
                    not self.tilemap.is_occupied_tile(neighbor)
                    and not self.tilemap.is_occupied_tile(bl)
                    and not self.tilemap.is_occupied_tile(tr)
                    and not self.tilemap.is_occupied_tile(br)
                ):
                    out.append(neighbor)
        return out

    def search(self, start, end):
        start, end = tuple(start), tuple(end)
        open_heap = [(euclidean(start, end), 0, start)]
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
            for n in self.__neighbors(current):
                if n in closed:
                    continue
                step = math.sqrt(2) if current[0] != n[0] and current[1] != n[1] else 1.0
                tentative = g_score[current] + step
                if n not in g_score or tentative < g_score[n]:
                    g_score[n] = tentative
                    came_from[n] = current
                    counter += 1
                    heapq.heappush(open_heap, (tentative + euclidean(n, end), counter, n))
        return None

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
