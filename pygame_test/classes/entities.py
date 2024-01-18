import pygame
import os
import sys
from dotenv import load_dotenv
load_dotenv()
MODULE_PATH = os.getenv('MODULE_PATH')
sys.path.insert(1, MODULE_PATH)
from physics.physics import PhysicsForces



class PhysicsEntity:
    def __init__(self, game, e_type, pos, size, mass = 1):
        self.game = game
        self.type = e_type
        self.pos = list(pos)
        self.size = size
        self.velocity = [0, 0]
        self.action = ''
        self.anim_offset = (0,0)
        self.flip = False
        self.set_action('idle')
        self.collisions = {'top': False, 'bottom': False, 'left': False, 'right': False}
        self.physics = PhysicsForces(self)
        self.mass = mass

    def rect(self):
        return pygame.Rect(*self.pos, *self.size)

    def set_action(self, action):
        if action != self.action:
            self.action = action
            self.animation = self.game.assets[self.type + '/' + self.action].copy()
            #self.animation.add_callback_func(10, lambda: self.animation.pause_animation())
            #self.animation.set_backwards()

    def update(self, tilemap, movement):
        self.collisions = {'top': False, 'bottom': False, 'left': False, 'right': False}
        frame_movement = (movement[0] + self.velocity[0], movement[1] + self.velocity[1])
        
        self.pos[0] += frame_movement[0]
        entity_rect = self.rect()
        for rect in tilemap.physics_rects_around(self.pos):
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
        for rect in tilemap.physics_rects_around(self.pos):
            if entity_rect.colliderect(rect):
                if frame_movement[1] > 0:
                    entity_rect.bottom = rect.top
                    self.collisions['bottom'] = True
                if frame_movement[1] < 0:
                    entity_rect.top = rect.bottom
                    self.collisions['top'] = True
                self.pos[1] = entity_rect.y + 8

        self.physics.gravity(self)
        #self.physics.move_towards(self, (10, 10), 0.5)
        if self.collisions['top'] or self.collisions['bottom']:
            self.velocity[1] = 0

        if movement[0] > 0:
            self.flip = False
        if movement[0] < 0:
            self.flip = True
        self.animation.update_frame()

    def render(self, surf, offset = (0,0)):
        if self.animation.is_finished():
            #self.set_action('idle')
            print('finished')
        else:
            surf.blit(pygame.transform.flip(self.animation.anim_image(), self.flip, False), (self.pos[0] - offset[0] + self.anim_offset[0], self.pos[1] - offset[1] + self.anim_offset[1]))


class Player(PhysicsEntity):
    def __init__(self, game, pos, size):
        super().__init__(game, 'player', pos, size)

    def update(self, tilemap, movement=(0,0)):
        super().update(tilemap, movement)

        if movement[0] != 0:
            self.set_action('run')
        else:
            self.set_action('idle')

        