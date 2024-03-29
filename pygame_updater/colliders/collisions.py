import pygame
from typing import overload

class ComplexCollision:
    def __split_to_edges(self, points):
        edges = []
        for i in range(len(points)-1):
            edges.append((points[i], points[(i + 1)]))
        edges.append((points[-1], points[0]))

        return edges

    def __check_point_collision(self, points, xp, yp):
        #ray casting algorithm
        edges = self.__split_to_edges(points)
        counter = 0
        for edge in edges:
            (x1, y1), (x2, y2) = edge
            if (yp < y1) != (yp < y2) and (xp < x1 + ((yp - y1) / (y2 - y1))* (x2 - x1)):
                counter += 1
    
        return counter % 2 == 1
    
    def rect_collide_poly(self, polygon_coordinates: list, rect: pygame.Rect):
        return (
        self.__check_point_collision(polygon_coordinates, rect.x, rect.y) or
        self.__check_point_collision(polygon_coordinates, rect.x + rect.width, rect.y) or
        self.__check_point_collision(polygon_coordinates, rect.x, rect.y + rect.height) or
        self.__check_point_collision(polygon_coordinates, rect.x + rect.width, rect.y + rect.height)
    )


    def rect_collide_circle(self, circle_center: tuple, radius: float, rect: pygame.Rect):
        x, y = circle_center
        closest_x = max(rect.x, min(x, rect.x + rect.width))
        closest_y = max(rect.y, min(y, rect.y + rect.height))

        distance_x = closest_x - x
        distance_y = closest_y - y

        distance_squared = (distance_x * distance_x) + (distance_y * distance_y)

        return distance_squared <= (radius * radius)

    def point_collide_poly(self, polygon_coordinates: list, point: tuple):
        return self.__check_point_collision(polygon_coordinates, point[0], point[1])

    def collide_circles(self, circle1_center: tuple, radius1: float, circle2_center: tuple, radius2: float):
        x1, y1 = circle1_center
        x2, y2 = circle2_center
        collision_valid = (x1 - x2)**2 + (y1 - y2)**2 <= (radius1 + radius2)**2
        return collision_valid

    

    