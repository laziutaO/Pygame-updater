import sys
import pygame
from classes.entities import PhysicsEntity
from classes.utils import load_image
import os
from dotenv import load_dotenv
load_dotenv()
MODULE_PATH = os.getenv('MODULE_PATH')
sys.path.insert(1, MODULE_PATH)
from colliders.collisions import collidepoly 

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
            'player': load_image('entities/player.png')
        }
        self.position = [100, 100]
        
        self.player = PhysicsEntity(self, 'player', (100, 100), (15, 25))
        self.points = [(100, 100), (200, 50), (300, 150), (250, 300), (150, 350)]
        self.polygon_collider = pygame.draw.polygon(self.display, (255, 0, 0), self.points)

    

    def run(self):
        while True:
            self.display.fill((30, 130, 12))
            self.player.update((self.movement_hor[1] - self.movement_hor[0], self.movement_ver[1] - self.movement_ver[0]))
            
            self.player.render(self.display)

            player_rect = pygame.Rect(*self.player.pos, *self.player.size)
            polygon_collider = pygame.draw.polygon(self.display, (255, 0, 0), self.points)
            collision = collidepoly(self.points, player_rect)
            if collision:
                print("Rectangle collides with polygon")
            else:
                print("No collision")
            if player_rect.colliderect(self.collision_area):
                pygame.draw.rect(self.display, (255, 0, 0), self.collision_area)
            else:
                pygame.draw.rect(self.display, (0, 255, 0), self.collision_area)
            """self.image_pos[1] += (self.movement[1] - self.movement[0])*4
        
            image_rect = pygame.Rect(*self.image_pos, *self.image.get_size())
            if image_rect.colliderect(self.collision_area):
                pygame.draw.rect(self.screen, (255, 0, 0), self.collision_area)
            else:
                pygame.draw.rect(self.screen, (0, 255, 0), self.collision_area)

            self.screen.blit(self.image, self.image_pos)"""
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
                        self.movement_ver[0] = True
                    if event.key == pygame.K_DOWN:
                        self.movement_ver[1] = True
                if event.type == pygame.KEYUP:
                    if event.key == pygame.K_LEFT:
                        self.movement_hor[0] = False
                    if event.key == pygame.K_RIGHT:
                        self.movement_hor[1] = False
                    if event.key == pygame.K_UP:
                        self.movement_ver[0] = False
                    if event.key == pygame.K_DOWN:
                        self.movement_ver[1] = False
            
            self.screen.blit(pygame.transform.scale(self.display, self.screen.get_size()), (0, 0))
            pygame.display.update()
            self.clock.tick(60)

if __name__ == '__main__':
    Game().run()