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
from classes.entities import PhysicsEntity


class Player(PhysicsEntity):
    MAX_HP = 100
    ATTACK_RANGE = 36
    ATTACK_DAMAGE = 25
    ATTACK_COOLDOWN = 30
    ATTACK_HIT_FRAME = 8

    def __init__(self, game, pos, size):
        super().__init__(game, 'player', pos, size)
        self.anim_offset = (-8, 0)
        self.max_hp = self.MAX_HP
        self.hp = self.MAX_HP
        self.dead = False
        self.attacking = False
        self.attack_cooldown = 0
        self._attack_hit_done = False

    def take_damage(self, dmg):
        if self.dead:
            return
        self.hp -= dmg
        if self.hp <= 0:
            self.hp = 0
            self.dead = True
            self.attacking = False
            self.set_action('death')

    def attack(self):
        if self.dead or self.attacking or self.attack_cooldown > 0:
            return
        self.attacking = True
        self.attack_cooldown = self.ATTACK_COOLDOWN
        self._attack_hit_done = False
        self.set_action('attack')

    def _attack_hitbox(self):
        if self.flip:
            return pygame.Rect(self.pos[0] - self.ATTACK_RANGE, self.pos[1], self.ATTACK_RANGE, self.size[1])
        return pygame.Rect(self.pos[0] + self.size[0], self.pos[1], self.ATTACK_RANGE, self.size[1])

    def update_flip(self, movement):
        if movement[0] > 0:
            self.flip = False
        elif movement[0] < 0:
            self.flip = True

    def update(self, tilemap, movement=(0, 0), enemies=None):
        if self.dead:
            super().update(tilemap, (0, 0))
            return

        super().update(tilemap, movement)

        if self.attack_cooldown > 0:
            self.attack_cooldown -= 1

        if self.attacking:
            if not self._attack_hit_done and self.animation.get_frame() >= self.ATTACK_HIT_FRAME:
                hit = self._attack_hitbox()
                for e in (enemies or []):
                    if not e.dead and hit.colliderect(e.rect()):
                        e.take_damage(self.ATTACK_DAMAGE)
                self._attack_hit_done = True
            if self.animation.is_finished():
                self.attacking = False

        if self.attacking:
            self.set_action('attack')
        elif movement[0] != 0:
            self.set_action('run')
        else:
            self.set_action('idle')


