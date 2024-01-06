import sys
import pygame

class Game:
    def __init__(self):
        pygame.init()

        pygame.display.set_caption('test game')
        self.screen = pygame.display.set_mode((640, 480))

        self.clock = pygame.time.Clock()

        self.image = pygame.image.load('test-data/images/clouds/cloud_1.png')
        self.image.set_colorkey((0,0,0))
        self.image_pos = [100, 100]
        #self.image = pygame.transform.scale(self.image, (200, 200))
        self.movement = [False, False]

        self.collision_area = pygame.Rect(50, 50, 100, 100)
        
    def run(self):
        while True:
            self.screen.fill((30, 130, 12))

            self.image_pos[1] += (self.movement[1] - self.movement[0])*4
        
            image_rect = pygame.Rect(*self.image_pos, *self.image.get_size())
            if image_rect.colliderect(self.collision_area):
                pygame.draw.rect(self.screen, (255, 0, 0), self.collision_area)
            else:
                pygame.draw.rect(self.screen, (0, 255, 0), self.collision_area)

            self.screen.blit(self.image, self.image_pos)

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_UP:
                        self.movement[0] = True
                    if event.key == pygame.K_DOWN:
                        self.movement[1] = True
                if event.type == pygame.KEYUP:
                    if event.key == pygame.K_UP:
                        self.movement[0] = False
                    if event.key == pygame.K_DOWN:
                        self.movement[1] = False
            
            pygame.display.update()
            self.clock.tick(60)

if __name__ == '__main__':
    Game().run()