"""2D physics forces and motion helpers. All velocity/position arguments are
mutable lists `[x, y]`; methods modify them in place AND return them, so they
can be chained or used in functional style.
"""
import math


class PhysicsForces:

    def gravity(self, velocity:list[float], acceleration:float=0.1, terminal_velocity:float=5,
                direction: tuple[float, float]=(0, 1), dt:float=1.0) -> list[float]:
        """Accelerate `velocity` along `direction`, capping the projection on
        that axis at `terminal_velocity`. Default direction is downward.
        """
        if dt < 0:
            raise ValueError("dt cannot be negative")
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

    def jump(self, velocity:list[float], force:float, direction: tuple[float, float]=(0, -1)) -> list[float]:
        """Add an impulse of `force` along `direction`.
        Default direction is upward.
        """
        velocity[0] += direction[0] * force
        velocity[1] += direction[1] * force
        return velocity

    def apply_impulse(self, velocity:list[float], impulse:list[float], mass:float) -> list[float]:
        """v += impulse / mass. Mass must be > 0."""
        if mass <= 0:
            raise ValueError("mass must be greater than 0")
        velocity[0] += impulse[0] / mass
        velocity[1] += impulse[1] / mass
        return velocity

    def apply_force(self, velocity:list[float], force:list[float], mass:float, dt:float=1.0) -> list[float]:
        """Use for sustained forces where dt matters."""
        if mass <= 0:
            raise ValueError("mass must be greater than 0")
        if dt < 0:
            raise ValueError("dt cannot be negative")
        velocity[0] += force[0] * dt / mass
        velocity[1] += force[1] * dt / mass
        return velocity

    def apply_acceleration(self, velocity:list[float], acceleration:list[float], dt:float=1.0) -> list[float]:
        if dt < 0:
            raise ValueError("dt cannot be negative")
        velocity[0] += acceleration[0] * dt
        velocity[1] += acceleration[1] * dt
        return velocity

    def friction(self, velocity:list[float], coefficient:float, dt:float=1.0) -> list[float]:
        if coefficient <= 0:
            raise ValueError("coefficient must be greater than 0")
        if dt < 0:
            raise ValueError("dt cannot be negative")
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

    def drag(self, velocity:list[float], coefficient:float, dt:float=1.0) -> list[float]:
        """Quadratic air drag."""
        if coefficient <= 0:
            raise ValueError("coefficient must be greater than 0")
        if dt < 0:
            raise ValueError("dt cannot be negative")
        speed = math.hypot(velocity[0], velocity[1])
        if speed == 0:
            return velocity
        factor = coefficient * speed * dt
        velocity[0] -= velocity[0] * factor
        velocity[1] -= velocity[1] * factor
        return velocity


    def clamp_speed(self, velocity:list[float], max_speed:float) -> list[float]:
        """Limit velocity to `max_speed` without changing direction."""
        speed = math.hypot(velocity[0], velocity[1])
        if speed > max_speed > 0:
            scale = max_speed / speed
            velocity[0] *= scale
            velocity[1] *= scale
        return velocity

    def knockback(self, velocity:list[float], source_pos: tuple[float, float], target_pos: tuple[float, float], force:float) -> list[float]:
        """Push the body at `target_pos` directly away from `source_pos`
        with the given impulse."""
        dx = target_pos[0] - source_pos[0]
        dy = target_pos[1] - source_pos[1]
        dist = math.hypot(dx, dy)
        if dist == 0:
            return velocity
        velocity[0] += dx / dist * force
        velocity[1] += dy / dist * force
        return velocity

    def bounce(self, velocity:list[float], normal: tuple[float, float], restitution:float=1.0) -> list[float]:
        """Reflect velocity off a surface with unit `normal`. `restitution=1`
        is perfectly elastic;"""
        nx, ny = normal

        length = math.hypot(nx, ny)

        if length == 0:
            raise ValueError("normal vector cannot be zero")
        
        proj = velocity[0] * nx + velocity[1] * ny
        if proj >= 0:
            return velocity  
        velocity[0] -= (1.0 + restitution) * proj * nx
        velocity[1] -= (1.0 + restitution) * proj * ny
        return velocity


    def update_position(self, pos:list[float], velocity:list[float], dt:float=1.0) -> list[float]:
        """Semi-implicit Euler step for position: pos += v * dt."""
        if dt < 0:
            raise ValueError("dt cannot be negative")
        pos[0] += velocity[0] * dt
        pos[1] += velocity[1] * dt
        return pos
