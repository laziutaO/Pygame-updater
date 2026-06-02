import math
import random


class Wander:
    """Wander steering: smooth random meandering.
Holds a `_wander_angle` that jitters a little each frame, projected onto a circle
ahead of the agent — gives gradual direction change instead of teleport-randomness.
"""
    def __init__(self, max_speed:float=2.0, jitter:float=0.2,
                 wander_radius:float=20.0, wander_distance:float=30.0):
        self.max_speed = max_speed
        self.jitter = jitter
        self.wander_radius = wander_radius
        self.wander_distance = wander_distance
        self._wander_angle = random.uniform(0, math.tau)

    def velocity(self, pos: tuple, heading: tuple=(1.0, 0.0)):
        hx, hy = heading
        h_mag = math.hypot(hx, hy)
        if h_mag == 0:
            hx, hy = 1.0, 0.0
        else:
            hx, hy = hx / h_mag, hy / h_mag
        self._wander_angle += random.uniform(-self.jitter, self.jitter)
        cx = pos[0] + hx * self.wander_distance
        cy = pos[1] + hy * self.wander_distance
        target_x = cx + math.cos(self._wander_angle) * self.wander_radius
        target_y = cy + math.sin(self._wander_angle) * self.wander_radius
        dx, dy = target_x - pos[0], target_y - pos[1]
        d = math.hypot(dx, dy)
        if d == 0:
            return (0.0, 0.0)
        return (dx / d * self.max_speed, dy / d * self.max_speed)
