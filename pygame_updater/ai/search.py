class SearchAction:
    def __init__(self, tilemap = None):
        self.path = []
        self.path_index = 0
        self.finished = False
        self.tilemap = tilemap

    def heuristic(self, start, end):
        return abs(start[0] - end[0]) + abs(start[1] - end[1])

    def neighbors(self, current):
        neighbors = []
        for x in range(-1, 2):
            for y in range(-1, 2):
                if x == 0 and y == 0:
                    continue
                neighbor = (current[0] + x, current[1] + y)
                if self.tilemap is None or not self.tilemap.is_occupied_tile(neighbor):
                    neighbors.append(neighbor)

        return neighbors

    def lowest_f_score(self, open_list, f_score):
        return min(open_list, key=lambda node: f_score[node])

    def reconstruct_path(self, came_from, current):
        total_path = [current]
        while current in came_from:
            current = came_from[current]
            total_path.append(current)
        return total_path[::-1]

    def a_star(self, start, end):
        start = tuple(start)
        end = tuple(end)
        open_list = [start]
        closed_list = set()
        came_from = {}
        g_score = {start: 0}
        f_score = {start: self.heuristic(start, end)}

        while open_list:
            current = self.lowest_f_score(open_list, f_score)

            if current == end:
                return self.reconstruct_path(came_from, current)

            open_list.remove(current)
            closed_list.add(current)

            for neighbor in self.neighbors(current):
                if neighbor in closed_list:
                    continue

                tentative_g_score = g_score[current] + self.heuristic(current, neighbor)

                if neighbor not in open_list or tentative_g_score < g_score[neighbor]:
                    came_from[neighbor] = current
                    g_score[neighbor] = tentative_g_score
                    f_score[neighbor] = g_score[neighbor] + self.heuristic(neighbor, end)

                    if neighbor not in open_list:
                        open_list.append(neighbor)

        return None  # No path found
    
    def get_next_position(self, start, end):
        if self.path_index == len(self.path):
            self.path = self.a_star(start, end)
            self.path_index = 0
            if self.path == None:
                self.finished = True
                return start
        self.path_index += 1
        return self.path[self.path_index - 1]
    
