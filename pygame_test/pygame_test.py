import sys
import pygame
from classes.entities import *
from classes.utils import *
import os
from dotenv import load_dotenv
load_dotenv()
MODULE_PATH = os.getenv('MODULE_PATH')
sys.path.insert(1, MODULE_PATH)
from colliders.collisions import *
from animation.animations import *
from tilemaps.tilemap import *
from physics.physics import *

BASE_IMG_PATH = 'test-data/images/'

class Game:
    def __init__(self):
        pygame.init()

        pygame.display.set_caption('test game')
        self.screen = pygame.display.set_mode((640, 480))
        self.display = pygame.Surface((320, 240))
        self.clock = pygame.time.Clock()

        """self.image = pygame.image.load('test-data/images/clouds/cloud_1.png')
        self.image.set_colorkey((0,0,0))
        self.image_pos = [100, 100]"""
        self.collision_area = pygame.Rect(50, 50, 20, 20)
        #self.image = pygame.transform.scale(self.image, (200, 200))
        self.movement_hor = [False, False]
        self.movement_ver = [False, False]
        self.assets = {
            'grass': load_images(BASE_IMG_PATH + 'tiles/grass'),
            'stone': load_images(BASE_IMG_PATH + 'tiles/stone'),
            'player': load_image( BASE_IMG_PATH + 'entities/player.png'),
            'player/idle': Animation(load_images(BASE_IMG_PATH + 'entities/player/idle'), 5),
            'player/run': Animation(load_images(BASE_IMG_PATH + 'entities/player/run'), 5),
        }
        self.tilemap = Tilemap(16, ['grass', 'stone'])
        self.tilemap.fill_tilemap((3, 12), (8, 14), 'grass', variant=0, rotation=90)
        #self.tilemap.fill_tilemap_random((1, 3), (9, 6), ['grass', 'stone'], [0, 1, 2])
        self.tilemap.place_tile_ongrid((3, 11), 'stone', 0, 180)
        self.tilemap.place_tile_offgrid((50, 50), 'stone', 0, 45)
        self.tilemap.place_tile_offgrid((80, 50), 'grass', 0, 45)
        self.position = [100, 100]
        
        self.player = Player(self, (100, 100), (15, 25))
        self.points = [(100, 100), (200, 50), (300, 150), (250, 300), (150, 350)]
        #self.polygon_collider = pygame.draw.polygon(self.display, (255, 0, 0), self.points)
        self.scroll = [0, 0]
    

    def run(self):
        while True:
            self.display.fill((30, 130, 12))
            self.scroll[0] += (self.player.rect().centerx - self.display.get_width() / 2 - self.scroll[0])/30
            self.scroll[1] += (self.player.rect().centery - self.display.get_height() / 2 - self.scroll[1])/30
            render_scroll = [int(self.scroll[0]), int(self.scroll[1])]

            self.tilemap.render(self.display, self.assets, offset = render_scroll)
            self.player.update(self.tilemap, (self.movement_hor[1] - self.movement_hor[0], 0))
            self.player.render(self.display, offset = render_scroll)
            
            #player_rect = pygame.Rect(*self.player.pos, *self.player.size)
            #polygon_collider = pygame.draw.polygon(self.display, (255, 0, 0), self.points)
            """if player_rect.colliderect(self.collision_area):
                pygame.draw.rect(self.display, (255, 0, 0), self.collision_area)
            else:
                pygame.draw.rect(self.display, (0, 255, 0), self.collision_area)"""

            #circle = pygame.draw.circle(self.display, (255, 0, 0), (100, 100), 50)
            
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_LEFT:
                        self.movement_hor[0] = True
                    if event.key == pygame.K_RIGHT:
                        self.movement_hor[1] = True
                    if event.key == pygame.K_UP:
                        self.player.physics.jump(self.player, 5)
                    if event.key == pygame.K_DOWN:
                        self.player.physics.apply_impulse(self.player, (0.1, 0), self.player.mass)
                if event.type == pygame.KEYUP:
                    if event.key == pygame.K_LEFT:
                        self.movement_hor[0] = False
                    if event.key == pygame.K_RIGHT:
                        self.movement_hor[1] = False
            
            self.screen.blit(pygame.transform.scale(self.display, self.screen.get_size()), (0, 0))
            pygame.display.update()
            self.clock.tick(60)

if __name__ == '__main__':
    Game().run()