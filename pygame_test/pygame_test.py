import sys
sys.path.append("/home/oleksii/kpi/diploma/soft/Pygame-updater")
import pygame
from classes.entities import *
import os
import pygame_updater
from dotenv import load_dotenv
load_dotenv()
MODULE_PATH = os.getenv('MODULE_PATH')
sys.path.insert(1, MODULE_PATH)
from pygame_updater.colliders.collisions import *
from pygame_updater.animation.animations import *
from pygame_updater.tilemaps.tilemap import *
from pygame_updater.physics.physics import *
from pygame_updater.ai.search import *

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
BASE_IMG_PATH = os.path.join(BASE_DIR, 'test-data1/')

class Game:
    def __init__(self):
        pygame.init()

        pygame.display.set_caption('test game')
        self.screen = pygame.display.set_mode((640, 480))
        self.display = pygame.Surface((320, 240))
        self.clock = pygame.time.Clock()
        
        self.collision_area = pygame.Rect(50, 50, 20, 20)
        #self.image = pygame.transform.scale(self.image, (200, 200))
        self.movement_hor = [False, False]
        self.movement_ver = [False, False]
        self.assets = {
            'grass': load_images(BASE_IMG_PATH + 'images/tiles-objects/1 Tiles'),
            #'stone': load_images(BASE_IMG_PATH + 'images/tiels-objects/Tiles/Tile_02.png'),
            'player': load_image( BASE_IMG_PATH + 'player/idle/row-1-column-1.png'),
            'player/idle': Animation(load_images(BASE_IMG_PATH + 'player/idle'), 5),
            'player/run': Animation(load_images(BASE_IMG_PATH + 'player/run'), 5),
            
        }
        #tilemap test
        self.tilemap = Tilemap(16, ['grass'])
        self.tilemap.fill_tilemap((3, 12), (8, 18), 'grass', variant=0, rotation=0)
        self.tilemap.fill_tilemap((10, 5), (11, 15), 'grass', variant=1, rotation=0)
        #self.tilemap.fill_tilemap_random((1, 3), (9, 6), ['grass', 'stone'], [0, 1, 2])
        
     
        
        self.player = Player(self, (80, 110), (15, 25))
        self.astar = SearchAction(self.player.size[0], self.player.size[1], self.tilemap)
        self.collision = ComplexCollision()
        
        #self.polygon_collider = pygame.draw.polygon(self.display, (255, 0, 0), self.points)
        self.scroll = [0, 0]
    

    def run(self):
        while True:
            self.display.fill((50, 130, 12))

            self.scroll[0] += (self.player.rect().centerx - self.display.get_width() / 2 - self.scroll[0])/10
            self.scroll[1] += (self.player.rect().centery - self.display.get_height() / 2 - self.scroll[1])/10
            render_scroll = [int(self.scroll[0]), int(self.scroll[1])]

            self.tilemap.render(self.display, self.assets, offset = render_scroll)
            self.player.update(self.tilemap, (self.movement_hor[1] - self.movement_hor[0], 0))
            #ai test
            #self.player.update_position(self.astar.get_next_position(self.player.pos, (200, 110)), offset = render_scroll)
            self.player.render(self.display, offset = render_scroll)
            
            player_rect = pygame.Rect(*self.player.pos, *self.player.size)

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
                        self.player.physics.jump(self.player.velocity, 3)
                    if event.key == pygame.K_DOWN:
                        self.player.velocity = self.player.physics.apply_impulse(self.player.velocity, (0.1, 0), self.player.mass)
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