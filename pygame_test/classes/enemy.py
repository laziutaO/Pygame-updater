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

class Enemy(PhysicsEntity):
    MAX_HP = 50
    DETECT_RADIUS = 200
    ATTACK_RANGE = 40
    ATTACK_DAMAGE = 10
    ATTACK_COOLDOWN = 60
    ATTACK_HIT_FRAME = 12
    SPEED = 1
    REPLAN_INTERVAL = 30
    LOOK_AHEAD = 8

    def __init__(self, game, pos, size):
        super().__init__(game, 'enemy', pos, size)
        self.max_hp = self.MAX_HP
        self.hp = self.MAX_HP
        self.dead = False
        self.death_complete = False
        self.attacking = False
        self.attack_cooldown = 0
        self._attack_hit_done = False
        self.state = 'idle'
        self._search = SearchAction(int(size[0]), int(size[1]), game.tilemap)
        self._path = []
        self._path_idx = 0
        self._replan = 0

    def take_damage(self, dmg):
        if self.dead:
            return
        self.hp -= dmg
        if self.hp <= 0:
            self.hp = 0
            self.dead = True
            self.attacking = False
            self.state = 'dead'
            self.set_action('death')

    def _attack_hitbox(self):
        # enemy convention: flip=True means facing right
        if self.flip:
            return pygame.Rect(self.pos[0] + self.size[0], self.pos[1], self.ATTACK_RANGE, self.size[1])
        return pygame.Rect(self.pos[0] - self.ATTACK_RANGE, self.pos[1], self.ATTACK_RANGE, self.size[1])

    def update_flip(self, movement):
        if movement[0] < 0:
            self.flip = False
        elif movement[0] > 0:
            self.flip = True

    def update(self, tilemap, player):
        if self.dead:
            super().update(tilemap, (0, 0))
            if self.animation.is_finished():
                self.death_complete = True
            return

        movement_x = 0
        if not player.dead:
            dx = player.rect().centerx - self.rect().centerx
            dy = player.rect().centery - self.rect().centery
            dist = math.hypot(dx, dy)

            if self.state == 'idle' and dist <= self.DETECT_RADIUS:
                self.state = 'chase'

            if self.state == 'chase':
                if (dist <= self.ATTACK_RANGE and self.attack_cooldown <= 0
                        and not self.attacking):
                    self.attacking = True
                    self.attack_cooldown = self.ATTACK_COOLDOWN
                    self._attack_hit_done = False
                    self.flip = dx > 0
                    self.set_action('attack')

                if not self.attacking:
                    self._replan -= 1
                    if (self._replan <= 0 or not self._path
                            or self._path_idx >= len(self._path)):
                        new_path = self._search.search(
                            (int(self.pos[0]), int(self.pos[1])),
                            (int(player.pos[0]), int(player.pos[1])),
                        )
                        self._path = new_path or []
                        self._path_idx = 0
                        self._replan = self.REPLAN_INTERVAL
                    if len(self._path) >= 2:
                        look = min(self._path_idx + self.LOOK_AHEAD, len(self._path) - 1)
                        target = self._path[look]
                        if target[0] > self.pos[0] + 2:
                            movement_x = self.SPEED
                        elif target[0] < self.pos[0] - 2:
                            movement_x = -self.SPEED
                        self._path_idx += 1

        if self.attack_cooldown > 0:
            self.attack_cooldown -= 1

        super().update(tilemap, (0 if self.attacking else movement_x, 0))

        if self.attacking:
            if not self._attack_hit_done and self.animation.get_frame() >= self.ATTACK_HIT_FRAME:
                hit = self._attack_hitbox()
                if not player.dead and hit.colliderect(player.rect()):
                    player.take_damage(self.ATTACK_DAMAGE)
                self._attack_hit_done = True
            if self.animation.is_finished():
                self.attacking = False

        if self.attacking:
            self.set_action('attack')
        elif movement_x != 0:
            self.set_action('walking')
        else:
            self.set_action('idle')
    


        