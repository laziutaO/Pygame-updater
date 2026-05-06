"""Seek steering: produce a velocity vector that drives an agent toward a target."""
import math


class Seek:
    """Optionally decelerates inside `slow_radius` for an arrive-style stop."""
    def __init__(self, max_speed=2.0, slow_radius=0.0):
        self.max_speed = max_speed
        self.slow_radius = slow_radius

    def velocity(self, pos, target):
        dx = target[0] - pos[0]
        dy = target[1] - pos[1]
        dist = math.hypot(dx, dy)
        if dist == 0:
            return (0.0, 0.0)
        speed = self.max_speed
        if self.slow_radius > 0 and dist < self.slow_radius:
            speed *= dist / self.slow_radius
        return (dx / dist * speed, dy / dist * speed)
