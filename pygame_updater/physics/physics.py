"""2D physics forces and motion helpers. All velocity/position arguments are
mutable lists `[x, y]`; methods modify them in place AND return them, so they
can be chained or used in functional style.

`dt` defaults to 1.0 so existing fixed-frame callers keep working unchanged.
Pass the real frame delta (seconds) for frame-rate-independent simulation.
"""
import math


class PhysicsForces:
    # ---------- gravity / jump (backward-compatible) ----------

    def gravity(self, velocity, acceleration=0.1, terminal_velocity=5,
                direction=(0, 1), dt=1.0):
        """Accelerate `velocity` along `direction`, capping the projection on
        that axis at `terminal_velocity`. Default direction is downward, so
        the call `gravity(v, 0.1, 5)` is unchanged from the original API.
        """
        dx, dy = direction
        proj = velocity[0] * dx + velocity[1] * dy
        if proj < terminal_velocity:
            velocity[0] += dx * acceleration * dt
            velocity[1] += dy * acceleration * dt
        else:
            excess = proj - terminal_velocity
            velocity[0] -= dx * excess
            velocity[1] -= dy * excess
        return velocity

    def jump(self, velocity, force, direction=(0, -1)):
        """Add an instantaneous impulse of `force` along `direction`.
        Default direction is upward.
        """
        velocity[0] += direction[0] * force
        velocity[1] += direction[1] * force
        return velocity

    def apply_impulse(self, velocity, impulse, mass):
        """v += impulse / mass. Mass must be > 0."""
        velocity[0] += impulse[0] / mass
        velocity[1] += impulse[1] / mass
        return velocity

    # ---------- general force / acceleration ----------

    def apply_force(self, velocity, force, mass, dt=1.0):
        """Newton's 2nd law: v += F * dt / m. Use for sustained forces (wind,
        thrust, magnetism) where dt matters."""
        velocity[0] += force[0] * dt / mass
        velocity[1] += force[1] * dt / mass
        return velocity

    def apply_acceleration(self, velocity, acceleration, dt=1.0):
        """v += a * dt. Use when you already have an acceleration vector
        (e.g., constant gravity in arbitrary direction)."""
        velocity[0] += acceleration[0] * dt
        velocity[1] += acceleration[1] * dt
        return velocity

    # ---------- friction / drag ----------

    def friction(self, velocity, coefficient, dt=1.0):
        """Linear (Coulomb-style) friction: subtract a constant deceleration
        opposing motion. Snaps to zero when the friction step would reverse
        direction — useful for top-down movement where you want a clean stop.
        """
        speed = math.hypot(velocity[0], velocity[1])
        if speed == 0:
            return velocity
        decel = coefficient * dt
        if decel >= speed:
            velocity[0] = 0.0
            velocity[1] = 0.0
        else:
            scale = (speed - decel) / speed
            velocity[0] *= scale
            velocity[1] *= scale
        return velocity

    def drag(self, velocity, coefficient, dt=1.0):
        """Quadratic air drag: F = -k * |v| * v. Slows fast objects much more
        than slow ones - characteristic of projectiles in atmosphere."""
        speed = math.hypot(velocity[0], velocity[1])
        if speed == 0:
            return velocity
        factor = coefficient * speed * dt
        velocity[0] -= velocity[0] * factor
        velocity[1] -= velocity[1] * factor
        return velocity


    # ---------- clamps / impacts ----------

    def clamp_speed(self, velocity, max_speed):
        """Limit |v| to `max_speed` without changing direction."""
        speed = math.hypot(velocity[0], velocity[1])
        if speed > max_speed > 0:
            scale = max_speed / speed
            velocity[0] *= scale
            velocity[1] *= scale
        return velocity

    def knockback(self, velocity, source_pos, target_pos, force):
        """Push the body at `target_pos` directly away from `source_pos`
        with the given impulse magnitude."""
        dx = target_pos[0] - source_pos[0]
        dy = target_pos[1] - source_pos[1]
        dist = math.hypot(dx, dy)
        if dist == 0:
            return velocity
        velocity[0] += dx / dist * force
        velocity[1] += dy / dist * force
        return velocity

    def bounce(self, velocity, normal, restitution=1.0):
        """Reflect velocity off a surface with unit `normal`. `restitution=1`
        is perfectly elastic; `0` kills the normal component (sticks)."""
        nx, ny = normal
        proj = velocity[0] * nx + velocity[1] * ny
        if proj >= 0:
            return velocity  # already moving away from the surface
        velocity[0] -= (1.0 + restitution) * proj * nx
        velocity[1] -= (1.0 + restitution) * proj * ny
        return velocity


    # ---------- integration ----------

    def update_position(self, pos, velocity, dt=1.0):
        """Semi-implicit Euler step for position: pos += v * dt."""
        pos[0] += velocity[0] * dt
        pos[1] += velocity[1] * dt
        return pos
