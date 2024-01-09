import pygame

def collidepoly(poly: list, rect: pygame.Rect):
    return (
    check_point_collision(poly, rect.x, rect.y) or
    check_point_collision(poly, rect.x + rect.width, rect.y) or
    check_point_collision(poly, rect.x, rect.y + rect.height) or
    check_point_collision(poly, rect.x + rect.width, rect.y + rect.height)
)

def split_to_edges(points):
    edges = []
    for i in range(len(points)-1):
        edges.append((points[i], points[(i + 1)]))
    edges.append((points[-1], points[0]))

    return edges

def check_point_collision(points, xp, yp):
    edges = split_to_edges(points)
    counter = 0
    for edge in edges:
        (x1, y1), (x2, y2) = edge
        if (yp < y1) != (yp < y2) and (xp < x1 + ((yp - y1) / (y2 - y1))* (x2 - x1)):
            counter += 1
    print("players pos: ", xp, yp)
    print(counter)    
    return counter % 2 == 1

    