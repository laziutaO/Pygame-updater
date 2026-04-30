import math
import os
import sys
import pygame
from dotenv import load_dotenv
load_dotenv()
MODULE_PATH = os.getenv('MODULE_PATH')
sys.path.insert(1, MODULE_PATH)
from pygame_updater.physics.physics import PhysicsForces
from pygame_updater.ai.search import SearchAction


class PhysicsEntity:
    def __init__(self, game, e_type, pos, size, mass=1):
        self.game = game
        self.type = e_type
        self.pos = list(pos)
        self.size = size
        self.velocity = [0, 0]
        self.action = ''
        self.anim_offset = (0, 0)
        self._ground_frames = 0
        self.flip = False
        self.set_action('idle')
        self.collisions = {'top': False, 'bottom': False, 'left': False, 'right': False}
        self.physics = PhysicsForces()
        self.mass = mass

    def rect(self):
        return pygame.Rect(*self.pos, *self.size)

    def _nearby_rects(self, tilemap):
        seen = {}
        for px, py in (
            (self.pos[0],                self.pos[1]),
            (self.pos[0] + self.size[0], self.pos[1]),
            (self.pos[0],                self.pos[1] + self.size[1]),
            (self.pos[0] + self.size[0], self.pos[1] + self.size[1]),
        ):
            for r in tilemap.physics_rects_around((px, py)):
                seen[(r.x, r.y)] = r
        return seen.values()

    @property
    def grounded(self):
        return self._ground_frames > 0

    def set_action(self, action):
        if action != self.action:
            self.action = action
            self.animation = self.game.assets[self.type + '/' + self.action].copy()

    def update(self, tilemap, movement):
        self.collisions = {'top': False, 'bottom': False, 'left': False, 'right': False}
        frame_movement = (movement[0] + self.velocity[0], movement[1] + self.velocity[1])

        self.pos[0] += frame_movement[0]
        entity_rect = self.rect()
        for rect in self._nearby_rects(tilemap):
            if entity_rect.colliderect(rect):
                if frame_movement[0] > 0:
                    entity_rect.right = rect.left
                    self.collisions['right'] = True
                if frame_movement[0] < 0:
                    entity_rect.left = rect.right
                    self.collisions['left'] = True
                self.pos[0] = entity_rect.x

        self.pos[1] += frame_movement[1]
        entity_rect = self.rect()
        for rect in self._nearby_rects(tilemap):
            if entity_rect.colliderect(rect):
                if frame_movement[1] > 0:
                    entity_rect.bottom = rect.top
                    self.collisions['bottom'] = True
                if frame_movement[1] < 0:
                    entity_rect.top = rect.bottom
                    self.collisions['top'] = True
                self.pos[1] = entity_rect.y

        self.velocity = self.physics.gravity(self.velocity, 0.1, 5)

        if self.collisions['top'] or self.collisions['bottom']:
            self.velocity[1] = 0

        if self.collisions['bottom']:
            self._ground_frames = 5
        elif self._ground_frames > 0:
            self._ground_frames -= 1

        self.update_flip(movement)

        self.animation.update_frame()

    def update_flip(self, movement):
        pass

    def render(self, surf, offset=(0, 0)):
        surf.blit(
            pygame.transform.flip(self.animation.anim_image(), self.flip, False),
            (self.pos[0] - offset[0] + self.anim_offset[0], self.pos[1] - offset[1] + self.anim_offset[1])
        )

    def update_position(self, pos, offset=(0, 0)):
        self.pos = list(pos)
        self.render(self.game.display, offset)




