
class PhysicsForces:
    def gravity(self, velocity, acceleration = 0.1, terminal_velocity = 5):
        if velocity[1] < terminal_velocity:
            velocity[1] += acceleration
        else:
            velocity[1] = terminal_velocity
        return velocity

    def apply_impulse(self, velocity, impulse, mass):
        velocity[0] += impulse[0] / mass
        velocity[1] += impulse[1] / mass
        return velocity


    def jump(self, velocity, force):
        velocity[1] -= force
        return velocity

            