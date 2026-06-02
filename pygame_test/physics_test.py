import math
import os
import sys

import pygame

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from pygame_updater.physics.physics import PhysicsForces


SCREEN_W, SCREEN_H = 1280, 720
FPS = 60

WHITE  = (240, 240, 240)
BLACK  = (15, 15, 15)
RED    = (220, 80, 80)
GREEN  = (80, 200, 120)
BLUE   = (80, 140, 220)
YELLOW = (240, 220, 80)
GRAY   = (110, 110, 110)
WATER  = (40, 60, 120)


class Scene:
    title = 'Scene'

    def __init__(self, surface, font):
        self.surface = surface
        self.font = font
        self.physics = PhysicsForces()
        self.done = False

    def handle_event(self, event):
        if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
            self.done = True

    def update(self, dt):
        pass

    def draw(self):
        pass

    def label(self, text, pos=(10, 10), color=WHITE):
        self.surface.blit(self.font.render(text, True, color), pos)


class GravityScene(Scene):
    title = 'gravity (a=800, terminal=400; SPACE = reset)'

    def __init__(self, surface, font):
        super().__init__(surface, font)
        self.ground_y = SCREEN_H - 40
        self._reset()

    def _reset(self):
        self.pos = [SCREEN_W / 2, 60.0]
        self.velocity = [0.0, 0.0]

    def handle_event(self, event):
        super().handle_event(event)
        if event.type == pygame.KEYDOWN and event.key == pygame.K_SPACE:
            self._reset()

    def update(self, dt):
        self.physics.gravity(self.velocity, 800, 400, dt=dt)
        self.physics.update_position(self.pos, self.velocity, dt=dt)
        if self.pos[1] >= self.ground_y:
            self.pos[1] = self.ground_y
            self.velocity[1] = 0.0

    def draw(self):
        pygame.draw.line(self.surface, GRAY, (0, self.ground_y), (SCREEN_W, self.ground_y), 1)
        pygame.draw.circle(self.surface, YELLOW, (int(self.pos[0]), int(self.pos[1])), 16, 2)
        self.label(self.title)
        self.label(f'vy={self.velocity[1]:.1f}', (10, 30))


class JumpScene(Scene):
    title = 'jump (force=500 + gravity; SPACE = jump)'

    def __init__(self, surface, font):
        super().__init__(surface, font)
        self.ground_y = SCREEN_H - 40
        self.pos = [SCREEN_W / 2, self.ground_y]
        self.velocity = [0.0, 0.0]
        self.grounded = True

    def handle_event(self, event):
        super().handle_event(event)
        if event.type == pygame.KEYDOWN and event.key == pygame.K_SPACE and self.grounded:
            self.physics.jump(self.velocity, 500)
            self.grounded = False

    def update(self, dt):
        self.physics.gravity(self.velocity, 1500, 800, dt=dt)
        self.physics.update_position(self.pos, self.velocity, dt=dt)
        if self.pos[1] >= self.ground_y:
            self.pos[1] = self.ground_y
            self.velocity[1] = 0.0
            self.grounded = True

    def draw(self):
        pygame.draw.line(self.surface, GRAY, (0, self.ground_y), (SCREEN_W, self.ground_y), 1)
        pygame.draw.circle(self.surface, YELLOW, (int(self.pos[0]), int(self.pos[1])), 16, 2)
        self.label(self.title)
        self.label(f'vy={self.velocity[1]:.1f}  grounded={self.grounded}', (10, 30))


class ApplyImpulseScene(Scene):
    title = 'apply_impulse (click = impulse; heavier = slower)'

    def __init__(self, surface, font):
        super().__init__(surface, font)
        self.bodies = [
            {'pos': [200.0, 120.0], 'vel': [0.0, 0.0], 'mass': 1.0,  'color': YELLOW},
            {'pos': [200.0, 240.0], 'vel': [0.0, 0.0], 'mass': 3.0,  'color': BLUE},
            {'pos': [200.0, 360.0], 'vel': [0.0, 0.0], 'mass': 10.0, 'color': RED},
        ]

    def handle_event(self, event):
        super().handle_event(event)
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            click = pygame.mouse.get_pos()
            for body in self.bodies:
                dx = click[0] - body['pos'][0]
                dy = click[1] - body['pos'][1]
                d = math.hypot(dx, dy)
                if d > 0:
                    impulse = (dx / d * 300, dy / d * 300)
                    self.physics.apply_impulse(body['vel'], impulse, body['mass'])

    def update(self, dt):
        for body in self.bodies:
            self.physics.friction(body['vel'], 200, dt=dt)
            self.physics.update_position(body['pos'], body['vel'], dt=dt)

    def draw(self):
        for body in self.bodies:
            x, y = int(body['pos'][0]), int(body['pos'][1])
            pygame.draw.circle(self.surface, body['color'], (x, y), 16, 2)
            speed = math.hypot(body['vel'][0], body['vel'][1])
            self.label(f"m={body['mass']:.0f}  |v|={speed:.1f}", (x + 22, y - 8), body['color'])
        self.label(self.title)


class ApplyForceScene(Scene):
    title = 'apply_force (wind +X; F=80 on all; heavier = slower)'

    def __init__(self, surface, font):
        super().__init__(surface, font)
        self._spawn()

    def _spawn(self):
        self.bodies = [
            {'pos': [40.0, 120.0], 'vel': [0.0, 0.0], 'mass': 1.0,  'color': YELLOW},
            {'pos': [40.0, 240.0], 'vel': [0.0, 0.0], 'mass': 3.0,  'color': BLUE},
            {'pos': [40.0, 360.0], 'vel': [0.0, 0.0], 'mass': 10.0, 'color': RED},
        ]

    def handle_event(self, event):
        super().handle_event(event)
        if event.type == pygame.KEYDOWN and event.key == pygame.K_SPACE:
            self._spawn()

    def update(self, dt):
        for body in self.bodies:
            self.physics.apply_force(body['vel'], (80, 0), body['mass'], dt=dt)
            self.physics.update_position(body['pos'], body['vel'], dt=dt)

    def draw(self):
        for body in self.bodies:
            x, y = int(body['pos'][0]), int(body['pos'][1])
            pygame.draw.circle(self.surface, body['color'], (x, y), 16, 2)
            self.label(f"m={body['mass']:.0f}  vx={body['vel'][0]:.1f}",
                       (x + 22, y - 8), body['color'])
        self.label(f'{self.title}  -  SPACE = reset')


class ApplyAccelScene(Scene):
    title = 'apply_acceleration (arrow keys; friction when idle)'

    def __init__(self, surface, font):
        super().__init__(surface, font)
        self.pos = [SCREEN_W / 2, SCREEN_H / 2]
        self.velocity = [0.0, 0.0]

    def update(self, dt):
        keys = pygame.key.get_pressed()
        accel = [0.0, 0.0]
        if keys[pygame.K_LEFT]:  accel[0] = -600
        if keys[pygame.K_RIGHT]: accel[0] = 600
        if keys[pygame.K_UP]:    accel[1] = -600
        if keys[pygame.K_DOWN]:  accel[1] = 600
        if accel == [0.0, 0.0]:
            self.physics.friction(self.velocity, 600, dt=dt)
        else:
            self.physics.apply_acceleration(self.velocity, accel, dt=dt)
        self.physics.update_position(self.pos, self.velocity, dt=dt)
        self.pos[0] = max(20, min(SCREEN_W - 20, self.pos[0]))
        self.pos[1] = max(20, min(SCREEN_H - 20, self.pos[1]))

    def draw(self):
        pygame.draw.circle(self.surface, YELLOW,
                           (int(self.pos[0]), int(self.pos[1])), 16, 2)
        speed = math.hypot(self.velocity[0], self.velocity[1])
        self.label(self.title)
        self.label(f'speed={speed:.1f}', (10, 30))


class LaunchScene(Scene):
    """Click anywhere to launch the ball at `launch_speed` toward the click."""
    title = 'launch'
    launch_speed = 400

    def __init__(self, surface, font):
        super().__init__(surface, font)
        self.pos = [SCREEN_W / 2, SCREEN_H / 2]
        self.velocity = [0.0, 0.0]

    def handle_event(self, event):
        super().handle_event(event)
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            mx, my = pygame.mouse.get_pos()
            dx = mx - self.pos[0]
            dy = my - self.pos[1]
            d = math.hypot(dx, dy)
            if d > 0:
                self.velocity = [dx / d * self.launch_speed, dy / d * self.launch_speed]

    def apply_decay(self, dt):
        raise NotImplementedError

    def update(self, dt):
        self.apply_decay(dt)
        self.physics.update_position(self.pos, self.velocity, dt=dt)

    def draw(self):
        pygame.draw.circle(self.surface, YELLOW,
                           (int(self.pos[0]), int(self.pos[1])), 16, 2)
        speed = math.hypot(self.velocity[0], self.velocity[1])
        self.label(f'{self.title}  -  click to launch')
        self.label(f'speed={speed:.2f}', (10, 30))


class FrictionScene(LaunchScene):
    title = 'friction (linear μ=600 — snaps to 0)'

    def apply_decay(self, dt):
        self.physics.friction(self.velocity, 600, dt=dt)


class DragScene(LaunchScene):
    title = 'drag (quadratic k=0.005 — fast slows fast)'
    launch_speed = 600

    def apply_decay(self, dt):
        self.physics.drag(self.velocity, 0.005, dt=dt)


class ClampSpeedScene(Scene):
    title = 'clamp_speed (max=250; arrow keys accelerate)'

    def __init__(self, surface, font):
        super().__init__(surface, font)
        self.pos = [SCREEN_W / 2, SCREEN_H / 2]
        self.velocity = [0.0, 0.0]

    def update(self, dt):
        keys = pygame.key.get_pressed()
        accel = [0.0, 0.0]
        if keys[pygame.K_LEFT]:  accel[0] = -800
        if keys[pygame.K_RIGHT]: accel[0] = 800
        if keys[pygame.K_UP]:    accel[1] = -800
        if keys[pygame.K_DOWN]:  accel[1] = 800
        self.physics.apply_acceleration(self.velocity, accel, dt=dt)
        self.physics.clamp_speed(self.velocity, 250)
        self.physics.update_position(self.pos, self.velocity, dt=dt)
        self.pos[0] = self.pos[0] % SCREEN_W
        self.pos[1] = self.pos[1] % SCREEN_H

    def draw(self):
        pygame.draw.circle(self.surface, YELLOW,
                           (int(self.pos[0]), int(self.pos[1])), 16, 2)
        speed = math.hypot(self.velocity[0], self.velocity[1])
        self.label(self.title)
        self.label(f'speed={speed:.1f} / 250', (10, 30))


class KnockbackScene(Scene):
    title = 'knockback (click = explosion source)'

    def __init__(self, surface, font):
        super().__init__(surface, font)
        self.pos = [SCREEN_W / 2, SCREEN_H / 2]
        self.velocity = [0.0, 0.0]
        self.last_source = None

    def handle_event(self, event):
        super().handle_event(event)
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            source = pygame.mouse.get_pos()
            self.physics.knockback(self.velocity, source, self.pos, 350)
            self.last_source = source

    def update(self, dt):
        self.physics.friction(self.velocity, 300, dt=dt)
        self.physics.update_position(self.pos, self.velocity, dt=dt)
        self.pos[0] = max(20, min(SCREEN_W - 20, self.pos[0]))
        self.pos[1] = max(20, min(SCREEN_H - 20, self.pos[1]))

    def draw(self):
        if self.last_source is not None:
            pygame.draw.circle(self.surface, RED, self.last_source, 6)
        pygame.draw.circle(self.surface, YELLOW,
                           (int(self.pos[0]), int(self.pos[1])), 16, 2)
        speed = math.hypot(self.velocity[0], self.velocity[1])
        self.label(self.title)
        self.label(f'speed={speed:.1f}', (10, 30))


class BounceScene(Scene):
    title = 'bounce'

    def __init__(self, surface, font):
        super().__init__(surface, font)
        self.restitution = 1.0
        self.radius = 18
        self._reset()

    def _reset(self):
        self.pos = [120.0, 120.0]
        self.velocity = [220.0, 160.0]

    def handle_event(self, event):
        super().handle_event(event)
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_1:
                self.restitution = 1.0; self._reset()
            elif event.key == pygame.K_2:
                self.restitution = 0.7; self._reset()
            elif event.key == pygame.K_3:
                self.restitution = 0.4; self._reset()

    def update(self, dt):
        self.physics.update_position(self.pos, self.velocity, dt=dt)
        if self.pos[0] - self.radius < 0:
            self.pos[0] = self.radius
            self.physics.bounce(self.velocity, (1, 0), self.restitution)
        if self.pos[0] + self.radius > SCREEN_W:
            self.pos[0] = SCREEN_W - self.radius
            self.physics.bounce(self.velocity, (-1, 0), self.restitution)
        if self.pos[1] - self.radius < 0:
            self.pos[1] = self.radius
            self.physics.bounce(self.velocity, (0, 1), self.restitution)
        if self.pos[1] + self.radius > SCREEN_H:
            self.pos[1] = SCREEN_H - self.radius
            self.physics.bounce(self.velocity, (0, -1), self.restitution)

    def draw(self):
        pygame.draw.rect(self.surface, GRAY,
                         pygame.Rect(0, 0, SCREEN_W, SCREEN_H), 2)
        pygame.draw.circle(self.surface, YELLOW,
                           (int(self.pos[0]), int(self.pos[1])), self.radius, 2)
        speed = math.hypot(self.velocity[0], self.velocity[1])
        self.label(f'{self.title}  -  e={self.restitution}')
        self.label(f'speed={speed:.1f}', (10, 30))





class UpdatePositionScene(Scene):
    title = 'update_position'

    def __init__(self, surface, font):
        super().__init__(surface, font)
        self._reset()

    def _reset(self):
        self.pos = [40.0, SCREEN_H / 2]
        self.velocity = [120.0, 60.0]

    def handle_event(self, event):
        super().handle_event(event)
        if event.type == pygame.KEYDOWN and event.key == pygame.K_SPACE:
            self._reset()

    def update(self, dt):
        self.physics.update_position(self.pos, self.velocity, dt=dt)
        if self.pos[0] > SCREEN_W or self.pos[1] > SCREEN_H:
            self._reset()

    def draw(self):
        pygame.draw.circle(self.surface, YELLOW,
                           (int(self.pos[0]), int(self.pos[1])), 16, 2)
        self.label(f'{self.title}  -  SPACE = reset')
        self.label(f'pos=({self.pos[0]:.1f}, {self.pos[1]:.1f})  '
                   f'v=({self.velocity[0]:.0f}, {self.velocity[1]:.0f})', (10, 30))


SCENES = [
    GravityScene,
    JumpScene,
    ApplyImpulseScene,
    ApplyForceScene,
    ApplyAccelScene,
    FrictionScene,
    DragScene,
    ClampSpeedScene,
    KnockbackScene,
    BounceScene,
    UpdatePositionScene,
]


class Menu:
    def __init__(self, surface, font):
        self.surface = surface
        self.font = font
        self.heading_font = pygame.font.SysFont('monospace', 18, bold=True)
        self.choice = None
        self.done = False

    def handle_event(self, event):
        if event.type == pygame.QUIT:
            self.done = True
            return
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                self.done = True
                return
            if pygame.K_1 <= event.key <= pygame.K_9:
                idx = event.key - pygame.K_1
            elif event.key == pygame.K_0:
                idx = 9
            elif event.key == pygame.K_q:
                idx = 10
            elif event.key == pygame.K_w:
                idx = 11
            elif event.key == pygame.K_e:
                idx = 12
            elif event.key == pygame.K_r:
                idx = 13
            else:
                return
            if 0 <= idx < len(SCENES):
                self.choice = SCENES[idx]
                self.done = True

    def draw(self):
        self.surface.fill(BLACK)
        self.surface.blit(
            self.heading_font.render('Physics tests', True, WHITE),
            (20, 20),
        )
        keys = ['1', '2', '3', '4', '5', '6', '7', '8', '9', '0', 'Q', 'W', 'E', 'R']
        for i, scene_cls in enumerate(SCENES):
            key = keys[i] if i < len(keys) else '?'
            text = f'{key}. {scene_cls.title}'
            self.surface.blit(self.font.render(text, True, WHITE),
                              (40, 60 + i * 24))
        self.surface.blit(self.font.render('ESC = quit', True, GRAY),
                          (20, SCREEN_H - 24))


def _run_loop(target, surface, clock):
    while not target.done:
        dt = clock.tick(FPS) / 1000.0
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return False
            target.handle_event(event)
        if hasattr(target, 'update'):
            target.update(dt)
        surface.fill(BLACK)
        target.draw()
        pygame.display.flip()
    return True


def main():
    pygame.init()
    pygame.display.set_caption('physics_test')
    surface = pygame.display.set_mode((SCREEN_W, SCREEN_H))
    clock = pygame.time.Clock()
    font = pygame.font.SysFont('monospace', 14)

    while True:
        menu = Menu(surface, font)
        if not _run_loop(menu, surface, clock):
            break
        if menu.choice is None:
            break
        scene = menu.choice(surface, font)
        if not _run_loop(scene, surface, clock):
            break

    pygame.quit()


if __name__ == '__main__':
    main()
