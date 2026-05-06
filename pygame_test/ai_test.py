"""Demos for every function/class in pygame_updater/ai.

Run from project root:
    python pygame_test/ai_test.py

Each scene exercises one AI primitive. ESC returns to the menu / quits.
"""
import os
import random
import sys

import pygame

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from pygame_updater.ai.search.astar import astar, GridGraph
from pygame_updater.ai.search.bfs import bfs
from pygame_updater.ai.search.dijkstra import dijkstra
from pygame_updater.ai.search.jps import jps
from pygame_updater.ai.steering.seek import Seek
from pygame_updater.ai.steering.wander import Wander
from pygame_updater.ai.navigation.flow_field import FlowField
from pygame_updater.ai.utils.los import line_of_sight
from pygame_updater.ai.utils.smoothing import smooth_path


SCREEN_W, SCREEN_H = 640, 480
FPS = 60
CELL = 32
GRID_W = SCREEN_W // CELL   # 20
GRID_H = SCREEN_H // CELL   # 15

WHITE  = (240, 240, 240)
BLACK  = (15, 15, 15)
RED    = (220, 80, 80)
GREEN  = (80, 200, 120)
BLUE   = (80, 140, 220)
YELLOW = (240, 220, 80)
GRAY   = (110, 110, 110)
DIM    = (40, 40, 40)


class Scene:
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


# ---------- Grid base ----------

class GridScene(Scene):
    """Shared grid + wall-toggle behavior."""
    default_walls = ()

    def __init__(self, surface, font):
        super().__init__(surface, font)
        self.walls = set(self.default_walls)

    def passable(self, cell):
        if not (0 <= cell[0] < GRID_W and 0 <= cell[1] < GRID_H):
            return False
        return cell not in self.walls

    def blocked(self, cell):
        return cell in self.walls or not (0 <= cell[0] < GRID_W and 0 <= cell[1] < GRID_H)

    def mouse_cell(self):
        mx, my = pygame.mouse.get_pos()
        return (mx // CELL, my // CELL)

    def cell_center(self, cell):
        return (cell[0] * CELL + CELL // 2, cell[1] * CELL + CELL // 2)

    def is_protected(self, cell):
        return False

    def handle_event(self, event):
        super().handle_event(event)
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            cell = self.mouse_cell()
            if self.is_protected(cell):
                return
            if cell in self.walls:
                self.walls.remove(cell)
            else:
                self.walls.add(cell)

    def draw_grid(self):
        for x in range(GRID_W):
            for y in range(GRID_H):
                rect = pygame.Rect(x * CELL, y * CELL, CELL, CELL)
                if (x, y) in self.walls:
                    pygame.draw.rect(self.surface, GRAY, rect)
                pygame.draw.rect(self.surface, DIM, rect, 1)


# ---------- Pathfinding ----------

class PathfindScene(GridScene):
    title = 'pathfind'
    default_walls = tuple(
        [(x, 5) for x in range(5, 12)] +
        [(10, y) for y in range(2, 8)]
    )

    def __init__(self, surface, font):
        super().__init__(surface, font)
        self.start = (1, 1)
        self.graph = GridGraph(self.passable, allow_diagonal=True)

    def is_protected(self, cell):
        return cell == self.start

    def search(self, start, end):
        raise NotImplementedError

    def draw(self):
        self.draw_grid()
        end = self.mouse_cell()
        path = self.search(self.start, end) if self.passable(end) else None
        if path and len(path) >= 2:
            pts = [self.cell_center(c) for c in path]
            pygame.draw.lines(self.surface, YELLOW, False, pts, 2)
            for p in pts:
                pygame.draw.circle(self.surface, BLUE, p, 3)
        pygame.draw.circle(self.surface, GREEN, self.cell_center(self.start), 8)
        if self.passable(end):
            pygame.draw.circle(self.surface, BLUE, self.cell_center(end), 8, 2)
        self.label(self.title)
        self.label(f'nodes={len(path) if path else 0}', (10, 30))
        self.label('left-click toggles wall', (10, SCREEN_H - 24), GRAY)


class AStarScene(PathfindScene):
    title = 'astar'

    def search(self, start, end):
        return astar(self.graph, start, end)


class BFSScene(PathfindScene):
    title = 'bfs'

    def search(self, start, end):
        return bfs(self.graph, start, end)


class DijkstraScene(PathfindScene):
    title = 'dijkstra'

    def search(self, start, end):
        return dijkstra(self.graph, start, end)


class JPSScene(PathfindScene):
    title = 'jps (path = jump points only)'

    def search(self, start, end):
        return jps(self.graph, start, end)


# ---------- Steering ----------

class SeekScene(Scene):
    title = 'Seek (mouse = target; arrives at slow_radius)'

    def __init__(self, surface, font):
        super().__init__(surface, font)
        self.seek = Seek(max_speed=200.0, slow_radius=80.0)
        self.pos = [SCREEN_W / 2, SCREEN_H / 2]

    def update(self, dt):
        target = pygame.mouse.get_pos()
        vx, vy = self.seek.velocity(self.pos, target)
        self.pos[0] += vx * dt
        self.pos[1] += vy * dt

    def draw(self):
        target = pygame.mouse.get_pos()
        pygame.draw.circle(self.surface, BLUE, target, 6)
        pygame.draw.circle(self.surface, GRAY, target, self.seek.slow_radius, 1)
        pygame.draw.circle(self.surface, YELLOW,
                           (int(self.pos[0]), int(self.pos[1])), 12, 2)
        self.label(self.title)


class WanderScene(Scene):
    title = 'Wander (Reynolds-style; trail shown)'
    trail_max = 220

    def __init__(self, surface, font):
        super().__init__(surface, font)
        self.wander = Wander(max_speed=140.0, jitter=0.35,
                             wander_radius=24.0, wander_distance=36.0)
        self.pos = [SCREEN_W / 2, SCREEN_H / 2]
        self.heading = (1.0, 0.0)
        self.trail = []

    def update(self, dt):
        vx, vy = self.wander.velocity(self.pos, self.heading)
        if vx != 0 or vy != 0:
            self.heading = (vx, vy)
        self.pos[0] = (self.pos[0] + vx * dt) % SCREEN_W
        self.pos[1] = (self.pos[1] + vy * dt) % SCREEN_H
        self.trail.append((int(self.pos[0]), int(self.pos[1])))
        if len(self.trail) > self.trail_max:
            self.trail = self.trail[-self.trail_max:]

    def draw(self):
        for i in range(1, len(self.trail)):
            a, b = self.trail[i - 1], self.trail[i]
            if abs(a[0] - b[0]) > SCREEN_W // 2 or abs(a[1] - b[1]) > SCREEN_H // 2:
                continue  # skip wrap-around segments
            pygame.draw.line(self.surface, GRAY, a, b, 1)
        if self.trail:
            pygame.draw.circle(self.surface, YELLOW, self.trail[-1], 8, 2)
        self.label(self.title)


# ---------- Navigation ----------

class FlowFieldScene(GridScene):
    title = 'FlowField (left-click toggles wall; mouse = goal)'
    default_walls = tuple([(x, 7) for x in range(6, 14)])
    agent_count = 40
    agent_speed = 70.0

    def __init__(self, surface, font):
        super().__init__(surface, font)
        self.graph = GridGraph(self.passable, allow_diagonal=True)
        self.flow = FlowField(self.graph)
        self.last_target = None
        self.agents = [
            [random.uniform(0, SCREEN_W), random.uniform(0, SCREEN_H)]
            for _ in range(self.agent_count)
        ]

    def update(self, dt):
        target = self.mouse_cell()
        if self.passable(target) and target != self.last_target:
            self.flow.build(target)
            self.last_target = target
        for agent in self.agents:
            cell = (int(agent[0] // CELL), int(agent[1] // CELL))
            dx, dy = self.flow.direction(cell)
            agent[0] += dx * self.agent_speed * dt
            agent[1] += dy * self.agent_speed * dt
            agent[0] = max(0, min(SCREEN_W - 1, agent[0]))
            agent[1] = max(0, min(SCREEN_H - 1, agent[1]))

    def draw(self):
        self.draw_grid()
        for cell, (dx, dy) in self.flow.flow.items():
            cx, cy = self.cell_center(cell)
            pygame.draw.line(self.surface, BLUE,
                             (cx, cy), (cx + int(dx * 10), cy + int(dy * 10)), 1)
        for agent in self.agents:
            pygame.draw.circle(self.surface, YELLOW,
                               (int(agent[0]), int(agent[1])), 4)
        if self.last_target:
            pygame.draw.circle(self.surface, GREEN,
                               self.cell_center(self.last_target), 8, 2)
        self.label(self.title)


# ---------- Utils ----------

class LoSScene(GridScene):
    title = 'line_of_sight (left-click toggles wall)'
    default_walls = tuple(
        [(x, 5) for x in range(6, 12)] +
        [(12, y) for y in range(8, 12)]
    )

    def __init__(self, surface, font):
        super().__init__(surface, font)
        self.source = (3, 7)

    def is_protected(self, cell):
        return cell == self.source

    def draw(self):
        self.draw_grid()
        end = self.mouse_cell()
        sees = line_of_sight(self.source, end, self.blocked)
        color = GREEN if sees else RED
        pygame.draw.line(self.surface, color,
                         self.cell_center(self.source), self.cell_center(end), 2)
        pygame.draw.circle(self.surface, BLUE, self.cell_center(self.source), 6)
        pygame.draw.circle(self.surface, YELLOW, self.cell_center(end), 6)
        self.label(self.title)
        self.label(f'visible={sees}', (10, 30))


class SmoothingScene(GridScene):
    title = 'smooth_path (gray = raw A*, yellow = smoothed)'
    default_walls = tuple([(8, y) for y in range(2, 10)])

    def __init__(self, surface, font):
        super().__init__(surface, font)
        self.start = (1, 7)
        self.graph = GridGraph(self.passable, allow_diagonal=True)

    def is_protected(self, cell):
        return cell == self.start

    def draw(self):
        self.draw_grid()
        end = self.mouse_cell()
        raw = astar(self.graph, self.start, end) if self.passable(end) else None
        smooth = smooth_path(raw, self.blocked) if raw else None
        if raw and len(raw) >= 2:
            pygame.draw.lines(self.surface, GRAY, False,
                              [self.cell_center(c) for c in raw], 1)
        if smooth and len(smooth) >= 2:
            pts = [self.cell_center(c) for c in smooth]
            pygame.draw.lines(self.surface, YELLOW, False, pts, 2)
            for p in pts:
                pygame.draw.circle(self.surface, BLUE, p, 4)
        pygame.draw.circle(self.surface, GREEN, self.cell_center(self.start), 6)
        self.label(self.title)
        raw_n = len(raw) if raw else 0
        smooth_n = len(smooth) if smooth else 0
        self.label(f'raw={raw_n}  smoothed={smooth_n}', (10, 30))


# ---------- Menu / launcher ----------

SCENES = [
    AStarScene,
    BFSScene,
    DijkstraScene,
    JPSScene,
    SeekScene,
    WanderScene,
    FlowFieldScene,
    LoSScene,
    SmoothingScene,
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
            self.heading_font.render('AI tests', True, WHITE),
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
    pygame.display.set_caption('ai_test')
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
