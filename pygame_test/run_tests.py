import os
import sys

import pygame

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import physics_test
import collisions_test
import ai_test


SCREEN_W, SCREEN_H = 1280, 720
FPS = 60

WHITE = (240, 240, 240)
BLACK = (15, 15, 15)
GRAY  = (110, 110, 110)


SUITES = [
    ('Physics tests',   physics_test),
    ('Collision tests', collisions_test),
    ('AI tests',        ai_test),
]


class MainMenu:
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
            if 0 <= idx < len(SUITES):
                self.choice = SUITES[idx][1]
                self.done = True

    def draw(self):
        self.surface.fill(BLACK)
        self.surface.blit(
            self.heading_font.render('pygame-updater · Тест', True, WHITE),
            (20, 20),
        )
        for i, (label, _) in enumerate(SUITES):
            self.surface.blit(self.font.render(f'{i + 1}. {label}', True, WHITE),
                              (40, 90 + i * 32))
        self.surface.blit(self.font.render('ESC = quit', True, GRAY),
                          (20, SCREEN_H - 30))


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


def _run_suite(module, surface, clock, font):
    while True:
        menu = module.Menu(surface, font)
        if not _run_loop(menu, surface, clock):
            return False          
        if menu.choice is None:
            return True           
        scene = menu.choice(surface, font)
        if not _run_loop(scene, surface, clock):
            return False             


def main():
    pygame.init()
    pygame.display.set_caption('pygame_updater tests')
    surface = pygame.display.set_mode((SCREEN_W, SCREEN_H))
    clock = pygame.time.Clock()
    font = pygame.font.SysFont('monospace', 14)

    while True:
        menu = MainMenu(surface, font)
        if not _run_loop(menu, surface, clock):
            break                     
        if menu.choice is None:
            break                    
        if not _run_suite(menu.choice, surface, clock, font):
            break                     

    pygame.quit()


if __name__ == '__main__':
    main()
