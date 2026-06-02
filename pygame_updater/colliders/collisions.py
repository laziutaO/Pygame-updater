import math
import pygame
from typing import Protocol

class ComplexCollision:
    def __split_to_edges(self, points: list) -> list[tuple[tuple, tuple]]:
        edges = []
        for i in range(len(points)-1):
            edges.append((points[i], points[(i + 1)]))
        edges.append((points[-1], points[0]))

        return edges

    def __check_point_collision(self, points: list, xp: float, yp: float) -> bool:
        edges = self.__split_to_edges(points)
        counter = 0
        for edge in edges:
            (x1, y1), (x2, y2) = edge
            if (yp < y1) != (yp < y2) and (xp < x1 + ((yp - y1) / (y2 - y1))* (x2 - x1)):
                counter += 1

        return counter % 2 == 1

    def rect_collide_poly(self, polygon_coordinates: list, rect: pygame.Rect):
        corners = (
            (rect.x,              rect.y),
            (rect.x + rect.width, rect.y),
            (rect.x,              rect.y + rect.height),
            (rect.x + rect.width, rect.y + rect.height),
        )
        for cx, cy in corners:
            if self.__check_point_collision(polygon_coordinates, cx, cy):
                return True
        for vx, vy in polygon_coordinates:
            if rect.collidepoint(vx, vy):
                return True

        rect_edges = (
            (corners[0], corners[1]),  # top
            (corners[1], corners[3]),  # right
            (corners[3], corners[2]),  # bottom
            (corners[2], corners[0]),  # left
        )
        for ra, rb in rect_edges:
            for pa, pb in self.__split_to_edges(polygon_coordinates):
                if self.__segments_intersect(ra, rb, pa, pb):
                    return True
        return False

    @staticmethod
    def __segments_intersect(pr1: tuple, pr2: tuple, pp3: tuple, pp4: tuple) -> bool:
        """Using cross product orientation test(to determine if point lies ot the left, right or on the line)"""
        def ccw(a, b, c):
            return (c[1] - a[1]) * (b[0] - a[0]) - (b[1] - a[1]) * (c[0] - a[0])
        d1 = ccw(pp3, pp4, pr1)
        d2 = ccw(pp3, pp4, pr2)
        d3 = ccw(pr1, pr2, pp3)
        d4 = ccw(pr1, pr2, pp4)
        return (((d1 > 0 and d2 < 0) or (d1 < 0 and d2 > 0))
                and ((d3 > 0 and d4 < 0) or (d3 < 0 and d4 > 0)))


    def rect_collide_circle(self, circle_center: tuple, radius: float, rect: pygame.Rect) -> bool:
        x, y = circle_center
        closest_x = max(rect.x, min(x, rect.x + rect.width))
        closest_y = max(rect.y, min(y, rect.y + rect.height))

        distance_x = closest_x - x
        distance_y = closest_y - y

        distance_squared = (distance_x * distance_x) + (distance_y * distance_y)

        return distance_squared <= (radius * radius)

    def point_collide_poly(self, polygon_coordinates: list, point: tuple) -> bool:
        return self.__check_point_collision(polygon_coordinates, point[0], point[1])

    def collide_circles(self, circle1_center: tuple, radius1: float, circle2_center: tuple, radius2: float) -> bool:
        x1, y1 = circle1_center
        x2, y2 = circle2_center
        collision_valid = (x1 - x2)**2 + (y1 - y2)**2 <= (radius1 + radius2)**2
        return collision_valid


class Collision:
    """Result of a narrow-phase test. `normal` is a unit vector pointing from body_a toward body_b."""
    def __init__(self, body_a, body_b, normal=(0.0, 0.0), penetration=0.0, restitution=1.0):
        self.body_a = body_a
        self.body_b = body_b
        self.normal = normal
        self.penetration = penetration
        self.restitution = restitution


class CircleLike(Protocol):
    center: tuple[float, float]
    radius: float

class CollisionSystem:

    def __init__(self):
        self._cc = ComplexCollision()
        self._enter_callbacks = []
        self._exit_callbacks = []
        self._active = {}

    def on_collision_enter(self, callback: callable):
        self._enter_callbacks.append(callback)

    def on_collision_exit(self, callback: callable):
        self._exit_callbacks.append(callback)

    @staticmethod
    def broad_phase(bodies: list) -> list[tuple]:
        """Returns list of (body_a, body_b) pairs whose rects overlap."""
        pairs = []
        n = len(bodies)
        for i in range(n):
            for j in range(i + 1, n):
                if bodies[i].rect.colliderect(bodies[j].rect):
                    pairs.append((bodies[i], bodies[j]))
        return pairs

    def narrow_phase(self, body_a, body_b) -> Collision | None:
        """Precise check between two bodies. Returns a Collision or None."""
        sa = getattr(body_a, 'shape', 'rect')
        sb = getattr(body_b, 'shape', 'rect')
        if sa == 'rect' and sb == 'rect':
            return self._rect_rect(body_a, body_b)
        if sa == 'circle' and sb == 'circle':
            return self._circle_circle(body_a, body_b)
        if {sa, sb} == {'circle', 'rect'}:
            circle = body_a if sa == 'circle' else body_b
            rect_b = body_b if sa == 'circle' else body_a
            return self._circle_rect(circle, rect_b, swap=(sa != 'circle'))
        if {sa, sb} == {'poly', 'rect'}:
            poly = body_a if sa == 'poly' else body_b
            rect_b = body_b if sa == 'poly' else body_a
            if self._cc.rect_collide_poly(poly.points, rect_b.rect):
                return Collision(body_a, body_b)
            return None
        
        # unsupported pair: degrade to AABB
        if body_a.rect.colliderect(body_b.rect):
            return Collision(body_a, body_b)
        return None

    @staticmethod
    def _rect_rect(a, b) -> Collision | None:
        if not a.rect.colliderect(b.rect):
            return None
        ox = min(a.rect.right, b.rect.right) - max(a.rect.left, b.rect.left)
        oy = min(a.rect.bottom, b.rect.bottom) - max(a.rect.top, b.rect.top)
        if ox < oy:
            normal = (1.0, 0.0) if a.rect.centerx < b.rect.centerx else (-1.0, 0.0)
            penetration = ox
        else:
            normal = (0.0, 1.0) if a.rect.centery < b.rect.centery else (0.0, -1.0)
            penetration = oy
        return Collision(a, b, normal, penetration)

    @staticmethod
    def _circle_circle(a: CircleLike, b: CircleLike) -> Collision | None:
        dx = b.center[0] - a.center[0]
        dy = b.center[1] - a.center[1]
        rs = a.radius + b.radius
        d2 = dx * dx + dy * dy
        if d2 > rs * rs:
            return None
        if d2 == 0:
            return Collision(a, b, (1.0, 0.0), rs)
        d = math.sqrt(d2)
        return Collision(a, b, (dx / d, dy / d), rs - d)

    def _circle_rect(self, circle: CircleLike, rect_b: pygame.Rect, swap=False) -> Collision | None:
        if not self._cc.rect_collide_circle(circle.center, circle.radius, rect_b.rect):
            return None
        cx, cy = circle.center
        nx = max(rect_b.rect.left, min(cx, rect_b.rect.right))
        ny = max(rect_b.rect.top, min(cy, rect_b.rect.bottom))
        dx, dy = cx - nx, cy - ny
        d2 = dx * dx + dy * dy
        if d2 == 0:
            normal = (1.0, 0.0)
            penetration = circle.radius
        else:
            d = math.sqrt(d2)
            normal = (-dx / d, -dy / d)  
            penetration = circle.radius - d
        if swap:
            return Collision(rect_b, circle, (-normal[0], -normal[1]), penetration)
        return Collision(circle, rect_b, normal, penetration)

    @staticmethod
    def resolve(collision:Collision):
        """Apply an impulse to separate two bodies"""
        if collision is None:
            return
        a, b = collision.body_a, collision.body_b
        nx, ny = collision.normal
        rvx = b.velocity[0] - a.velocity[0]
        rvy = b.velocity[1] - a.velocity[1]
        rel_n = rvx * nx + rvy * ny
        if rel_n > 0:
            return  # already separating
        inv_a = 1.0 / a.mass if a.mass else 0.0
        inv_b = 1.0 / b.mass if b.mass else 0.0
        denom = inv_a + inv_b
        if denom == 0:
            return
        j = -(1.0 + collision.restitution) * rel_n / denom
        a.velocity[0] -= j * nx * inv_a
        a.velocity[1] -= j * ny * inv_a
        b.velocity[0] += j * nx * inv_b
        b.velocity[1] += j * ny * inv_b

    def step(self, bodies: list)-> list[Collision]:
        """Run broad+narrow over bodies, return list of Collisions."""
        collisions = []
        current = {}
        for a, b in self.broad_phase(bodies):
            collision = self.narrow_phase(a, b)
            if collision is None:
                continue
            key = (id(a), id(b)) if id(a) < id(b) else (id(b), id(a))
            current[key] = (a, b)
            collisions.append(collision)
            if key not in self._active:
                for cb in self._enter_callbacks:
                    cb(a, b)
        for key, (a, b) in self._active.items():
            if key not in current:
                for cb in self._exit_callbacks:
                    cb(a, b)
        self._active = current
        return collisions
