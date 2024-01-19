
class PhysicsForces:
    def gravity(self, entity, acceleration = 0.1, terminal_velocity = 5):
        if entity.velocity[1] < terminal_velocity:
            entity.velocity[1] += acceleration
        else:
            entity.velocity[1] = terminal_velocity

    def move_towards(self, entity, target, speed):
        direction = (target[0] - entity.pos[0], target[1] - entity.pos[1])
        distance = (direction[0]**2 + direction[1]**2)**0.5
        direction = (direction[0] / distance, direction[1] / distance)
        entity.velocity = (direction[0] * speed, direction[1] * speed)

    def apply_impulse(self, entity, impulse, mass):
        entity.velocity[0] += impulse[0] / mass
        entity.velocity[1] += impulse[1] / mass

    def apply_friction(self, entity, friction_coeff=0.01):
        entity.velocity[0] *= (1 - friction_coeff)
        entity.velocity[1] *= (1 - friction_coeff)

    def jump(self, entity, force):
        entity.velocity[1] -= force

            