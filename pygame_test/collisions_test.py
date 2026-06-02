import os
import sys

import pygame

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from pygame_updater.colliders.collisions import (
    ComplexCollision,
    CollisionSystem,
)


SCREEN_W, SCREEN_H = 1280, 720
FPS = 60

WHITE  = (240, 240, 240)
BLACK  = (15, 15, 15)
RED    = (220, 80, 80)
GREEN  = (80, 200, 120)
BLUE   = (80, 140, 220)
YELLOW = (240, 220, 80)
GRAY   = (110, 110, 110)


class Body:
    """Duck-typed body that satisfies CollisionSystem's expectations."""
    def __init__(self, rect, shape='rect', center=None, radius=0,
                 points=None, velocity=(0, 0), mass=1.0, color=WHITE):
        self.rect = rect
        self.shape = shape
        self.center = list(center) if center is not None else None
        self.radius = radius
        self.points = points
        self.velocity = list(velocity)
        self.mass = mass
        self.color = color


class Scene:
    """Base scene. Subclasses override update/draw/handle_event."""
    title = 'Scene'

    def __init__(self, surface, font):
        self.surface = surface
        self.font = font
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


# ---------- ComplexCollision primitives ----------

class RectCircleScene(Scene):
    title = 'rect_collide_circle'

    def __init__(self, surface, font):
        super().__init__(surface, font)
        self.cc = ComplexCollision()
        self.rect = pygame.Rect(220, 180, 200, 120)
        self.radius = 40

    def draw(self):
        cx, cy = pygame.mouse.get_pos()
        hit = self.cc.rect_collide_circle((cx, cy), self.radius, self.rect)
        color = RED if hit else GREEN
        pygame.draw.rect(self.surface, color, self.rect, 2)
        pygame.draw.circle(self.surface, color, (cx, cy), self.radius, 2)
        self.label(f'{self.title}  -  move mouse')
        self.label(f'colliding={hit}', (10, 30))


class RectPolyScene(Scene):
    title = 'rect_collide_poly'

    def __init__(self, surface, font):
        super().__init__(surface, font)
        self.cc = ComplexCollision()
        self.poly = [(150, 100), (480, 130), (520, 320), (180, 380), (90, 240)]
        self.rect_size = (80, 50)

    def draw(self):
        mx, my = pygame.mouse.get_pos()
        rect = pygame.Rect(
            mx - self.rect_size[0] // 2,
            my - self.rect_size[1] // 2,
            *self.rect_size,
        )
        hit = self.cc.rect_collide_poly(self.poly, rect)
        color = RED if hit else GREEN
        pygame.draw.polygon(self.surface, color, self.poly, 2)
        pygame.draw.rect(self.surface, color, rect, 2)
        self.label(f'{self.title}  -  move mouse')
        self.label(f'colliding={hit}', (10, 30))


class PointPolyScene(Scene):
    title = 'point_collide_poly'

    def __init__(self, surface, font):
        super().__init__(surface, font)
        self.cc = ComplexCollision()
        self.poly = [(220, 100), (450, 200), (400, 400), (180, 360), (140, 220)]

    def draw(self):
        mx, my = pygame.mouse.get_pos()
        hit = self.cc.point_collide_poly(self.poly, (mx, my))
        color = RED if hit else GREEN
        pygame.draw.polygon(self.surface, color, self.poly, 2)
        pygame.draw.circle(self.surface, color, (mx, my), 4)
        self.label(f'{self.title}  -  mouse = point')
        self.label(f'inside={hit}', (10, 30))


class CircleCircleScene(Scene):
    title = 'collide_circles'

    def __init__(self, surface, font):
        super().__init__(surface, font)
        self.cc = ComplexCollision()
        self.center_a = (320, 240)
        self.r_a = 60
        self.r_b = 40

    def draw(self):
        center_b = pygame.mouse.get_pos()
        hit = self.cc.collide_circles(self.center_a, self.r_a, center_b, self.r_b)
        color = RED if hit else GREEN
        pygame.draw.circle(self.surface, color, self.center_a, self.r_a, 2)
        pygame.draw.circle(self.surface, color, center_b, self.r_b, 2)
        self.label(f'{self.title}  -  move mouse')
        self.label(f'colliding={hit}', (10, 30))


class BroadPhaseScene(Scene):
    title = 'broad_phase'

    def __init__(self, surface, font):
        super().__init__(surface, font)
        self.system = CollisionSystem()
        self.bodies = [
            Body(pygame.Rect(80, 80, 60, 60)),
            Body(pygame.Rect(300, 120, 80, 50)),
            Body(pygame.Rect(450, 300, 70, 70)),
            Body(pygame.Rect(160, 320, 90, 60)),
        ]
        self.cursor = Body(pygame.Rect(0, 0, 70, 50), color=YELLOW)

    def update(self, dt):
        self.cursor.rect.center = pygame.mouse.get_pos()

    def draw(self):
        all_bodies = self.bodies + [self.cursor]
        pairs = self.system.broad_phase(all_bodies)
        flagged = {id(b) for pair in pairs for b in pair}
        for body in all_bodies:
            color = RED if id(body) in flagged else GREEN
            pygame.draw.rect(self.surface, color, body.rect, 2)
        self.label(f'{self.title}  -  move mouse box')
        self.label(f'pairs={len(pairs)}', (10, 30))


class NarrowPhaseScene(Scene):
    title = 'narrow_phase (rect cursor vs rect / circle / poly)'

    def __init__(self, surface, font):
        super().__init__(surface, font)
        self.system = CollisionSystem()
        circle_center = (430, 140)
        circle_r = 50
        poly_pts = [(160, 320), (300, 280), (380, 380), (220, 420)]
        xs = [p[0] for p in poly_pts]
        ys = [p[1] for p in poly_pts]
        self.bodies = [
            Body(pygame.Rect(80, 100, 100, 70)),
            Body(
                pygame.Rect(circle_center[0] - circle_r, circle_center[1] - circle_r,
                            2 * circle_r, 2 * circle_r),
                shape='circle', center=circle_center, radius=circle_r,
            ),
            Body(
                pygame.Rect(min(xs), min(ys), max(xs) - min(xs), max(ys) - min(ys)),
                shape='poly', points=poly_pts,
            ),
        ]
        self.cursor_size = (50, 50)

    def draw(self):
        mx, my = pygame.mouse.get_pos()
        cursor = Body(pygame.Rect(
            mx - self.cursor_size[0] // 2,
            my - self.cursor_size[1] // 2,
            *self.cursor_size,
        ))
        for body in self.bodies:
            collision = self.system.narrow_phase(cursor, body)
            color = RED if collision else GREEN
            if body.shape == 'rect':
                pygame.draw.rect(self.surface, color, body.rect, 2)
            elif body.shape == 'circle':
                pygame.draw.circle(self.surface, color, body.center, body.radius, 2)
            elif body.shape == 'poly':
                pygame.draw.polygon(self.surface, color, body.points, 2)
        pygame.draw.rect(self.surface, YELLOW, cursor.rect, 2)
        self.label(self.title)


class ResolveScene(Scene):
    title = 'resolve (impulse exchange; SPACE = reset)'

    def __init__(self, surface, font):
        super().__init__(surface, font)
        self.system = CollisionSystem()
        self._spawn()

    def _spawn(self):
        ra, rb = 30, 35
        self.a = Body(
            pygame.Rect(150 - ra, 240 - ra, 2 * ra, 2 * ra),
            shape='circle', center=(150, 240), radius=ra,
            velocity=(140, 30), mass=1.0, color=BLUE,
        )
        self.b = Body(
            pygame.Rect(490 - rb, 250 - rb, 2 * rb, 2 * rb),
            shape='circle', center=(490, 250), radius=rb,
            velocity=(-110, -20), mass=1.5, color=YELLOW,
        )

    def handle_event(self, event):
        super().handle_event(event)
        if event.type == pygame.KEYDOWN and event.key == pygame.K_SPACE:
            self._spawn()

    def _integrate(self, body, dt):
        body.center[0] += body.velocity[0] * dt
        body.center[1] += body.velocity[1] * dt
        r = body.radius
        if body.center[0] - r < 0:
            body.center[0] = r
            body.velocity[0] *= -1
        if body.center[0] + r > SCREEN_W:
            body.center[0] = SCREEN_W - r
            body.velocity[0] *= -1
        if body.center[1] - r < 0:
            body.center[1] = r
            body.velocity[1] *= -1
        if body.center[1] + r > SCREEN_H:
            body.center[1] = SCREEN_H - r
            body.velocity[1] *= -1
        body.rect.center = (int(body.center[0]), int(body.center[1]))

    def update(self, dt):
        for body in (self.a, self.b):
            self._integrate(body, dt)
        collision = self.system.narrow_phase(self.a, self.b)
        if collision is None:
            return
        self.system.resolve(collision)
        # positional separation so the bodies don't sink into each other
        nx, ny = collision.normal
        push = collision.penetration / 2
        self.a.center[0] -= nx * push
        self.a.center[1] -= ny * push
        self.b.center[0] += nx * push
        self.b.center[1] += ny * push

    def draw(self):
        for body in (self.a, self.b):
            pygame.draw.circle(
                self.surface, body.color,
                (int(body.center[0]), int(body.center[1])),
                body.radius, 2,
            )
        self.label(self.title)


class EventsScene(Scene):
    title = 'on_collision_enter / on_collision_exit'

    def __init__(self, surface, font):
        super().__init__(surface, font)
        self.system = CollisionSystem()
        self.system.on_collision_enter(self._on_enter)
        self.system.on_collision_exit(self._on_exit)
        self.bodies = [
            Body(pygame.Rect(160 - 35, 200 - 35, 70, 70),
                 shape='circle', center=(160, 200), radius=35, color=GREEN),
            Body(pygame.Rect(430 - 40, 180 - 40, 80, 80),
                 shape='circle', center=(430, 180), radius=40, color=BLUE),
            Body(pygame.Rect(310 - 30, 360 - 30, 60, 60),
                 shape='circle', center=(310, 360), radius=30, color=YELLOW),
        ]
        self.cursor = Body(pygame.Rect(0, 0, 50, 50), color=WHITE)
        self.log = []

    def _name(self, body):
        return f'body@{id(body) % 1000:03d}'

    def _other(self, a, b):
        if a is self.cursor:
            return b
        if b is self.cursor:
            return a
        return None

    def _push(self, line):
        self.log.append(line)
        self.log = self.log[-8:]

    def _on_enter(self, a, b):
        other = self._other(a, b)
        if other is not None:
            self._push(f'ENTER  {self._name(other)}')

    def _on_exit(self, a, b):
        other = self._other(a, b)
        if other is not None:
            self._push(f'EXIT   {self._name(other)}')

    def update(self, dt):
        self.cursor.rect.center = pygame.mouse.get_pos()
        self.system.step(self.bodies + [self.cursor])

    def draw(self):
        for body in self.bodies:
            pygame.draw.circle(self.surface, body.color, body.center, body.radius, 2)
        pygame.draw.rect(self.surface, WHITE, self.cursor.rect, 2)
        self.label(f'{self.title}  -  drag mouse rect over circles')
        for i, line in enumerate(self.log):
            self.label(line, (10, 50 + i * 18), GRAY)


# ---------- Menu / launcher ----------

SCENES = [
    RectCircleScene,
    RectPolyScene,
    PointPolyScene,
    CircleCircleScene,
    BroadPhaseScene,
    NarrowPhaseScene,
    ResolveScene,
    EventsScene,
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
            idx = event.key - pygame.K_1
            if 0 <= idx < len(SCENES):
                self.choice = SCENES[idx]
                self.done = True

    def draw(self):
        self.surface.fill(BLACK)
        self.surface.blit(
            self.heading_font.render('Collision tests', True, WHITE),
            (20, 20),
        )
        for i, scene_cls in enumerate(SCENES):
            text = f'{i + 1}. {scene_cls.title}'
            self.surface.blit(self.font.render(text, True, WHITE),
                              (40, 70 + i * 28))
        self.surface.blit(
            self.font.render('ESC = quit', True, GRAY),
            (20, SCREEN_H - 30),
        )


def _run_loop(target, surface, clock):
    """Drive a Scene or Menu until it sets done=True. Returns False to quit app."""
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
    pygame.display.set_caption('collisions_test')
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
