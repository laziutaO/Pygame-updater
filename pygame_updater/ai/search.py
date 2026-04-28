import math
import heapq
from ..tilemaps.tilemap import Tilemap

class SearchAction:
    def __init__(self, entity_width: int, entity_height: int, tilemap: Tilemap = None):
        self.path = []
        self.path_index = 0
        self.finished = False
        self.tilemap = tilemap
        self.entity_width = entity_width
        self.entity_height = entity_height

    def __heuristic(self, start, end):
        dx = start[0] - end[0]
        dy = start[1] - end[1]
        return math.sqrt(dx * dx + dy * dy)

    def __step_cost(self, current, neighbor):
        return math.sqrt(2) if current[0] != neighbor[0] and current[1] != neighbor[1] else 1.0

    def __neighbors(self, current):
        neighbors = []
        for x in range(-1, 2):
            for y in range(-1, 2):
                if x == 0 and y == 0:
                    continue
                neighbor = (current[0] + x, current[1] + y)
                bottom_left = (neighbor[0], neighbor[1] + self.entity_height)
                top_right = (neighbor[0] + self.entity_width, neighbor[1])
                bottom_right = (top_right[0], bottom_left[1])
                if self.tilemap is None:
                    neighbors.append(neighbor)
                elif not self.tilemap.is_occupied_tile(neighbor) \
                    and not self.tilemap.is_occupied_tile(bottom_left) \
                    and not self.tilemap.is_occupied_tile(top_right) \
                    and not self.tilemap.is_occupied_tile(bottom_right):
                    neighbors.append(neighbor)
        return neighbors

    def __reconstruct_path(self, came_from, current):
        total_path = [current]
        while current in came_from:
            current = came_from[current]
            total_path.append(current)
        return total_path[::-1]

    def search(self, start: tuple, end: tuple):
        start = tuple(start)
        end = tuple(end)
        open_heap = [(self.__heuristic(start, end), start)]
        visited = set()
        came_from = {}
        g_score = {start: 0.0}

        while open_heap:
            _, current = heapq.heappop(open_heap)

            if current in visited:
                continue
            visited.add(current)

            if current == end:
                return self.__reconstruct_path(came_from, current)

            for neighbor in self.__neighbors(current):
                if neighbor in visited:
                    continue
                tentative_g = g_score[current] + self.__step_cost(current, neighbor)
                if neighbor not in g_score or tentative_g < g_score[neighbor]:
                    came_from[neighbor] = current
                    g_score[neighbor] = tentative_g
                    heapq.heappush(open_heap, (tentative_g + self.__heuristic(neighbor, end), neighbor))

        return None

    def get_next_position(self, start: tuple, end: tuple):
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
