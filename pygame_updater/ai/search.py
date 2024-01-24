from tilemaps.tilemap import Tilemap

class SearchAction:
    def __init__(self, entity_width: int, entity_height: int, tilemap: Tilemap = None):
        self.path = []
        self.path_index = 0
        self.finished = False
        self.tilemap = tilemap
        self.entity_width = entity_width
        self.entity_height = entity_height

    def __heuristic(self, start, end):
        return abs(start[0] - end[0]) + abs(start[1] - end[1])

    def __neighbors(self, current):
        neighbors = []
        for x in range(-1, 2):
            for y in range(-1, 2):
                if x == 0 and y == 0:
                    continue
                bottom_left = (current[0] + x, current[1] + y + self.entity_height)
                top_right = (current[0] + x + self.entity_width, current[1] + y)
                bottom_right = (top_right[0], bottom_left[1])
                neighbor = (current[0] + x, current[1] + y)
                if self.tilemap is None:
                    neighbors.append(neighbor)
                elif not self.tilemap.is_occupied_tile(neighbor) and not self.tilemap.is_occupied_tile(bottom_left) and not self.tilemap.is_occupied_tile(top_right) and not self.tilemap.is_occupied_tile(bottom_right):
                    neighbors.append(neighbor)

        return neighbors

    def __lowest_f_score(self, open_list, f_score):
        return min(open_list, key=lambda node: f_score[node])

    def __reconstruct_path(self, came_from, current):
        total_path = [current]
        while current in came_from:
            current = came_from[current]
            total_path.append(current)
        return total_path[::-1]

    def search(self, start:tuple, end:tuple):
        start = tuple(start)
        end = tuple(end)
        open_list = [start]
        closed_list = set()
        came_from = {}
        g_score = {start: 0}
        f_score = {start: self.__heuristic(start, end)}

        while open_list:
            current = self.__lowest_f_score(open_list, f_score)

            if current == end:
                return self.__reconstruct_path(came_from, current)

            open_list.remove(current)
            closed_list.add(current)

            for neighbor in self.__neighbors(current):
                if neighbor in closed_list:
                    continue

                tentative_g_score = g_score[current] + self.__heuristic(current, neighbor)

                if neighbor not in open_list or tentative_g_score < g_score[neighbor]:
                    came_from[neighbor] = current
                    g_score[neighbor] = tentative_g_score
                    f_score[neighbor] = g_score[neighbor] + self.__heuristic(neighbor, end)

                    if neighbor not in open_list:
                        open_list.append(neighbor)

        return None 
    
    def get_next_position(self, start:tuple, end:tuple):
        if self.path_index == len(self.path):
            self.path = self.search(start, end)
            self.path_index = 0
            if self.path == None:
                self.finished = True
                return start
        self.path_index += 1
        return self.path[self.path_index - 1]
    
