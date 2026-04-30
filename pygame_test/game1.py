import sys
import os
import pygame

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from pygame_updater.animation.animations import Animation, load_image, load_images
from pygame_updater.tilemaps.tilemap import Tilemap

from classes.enemy import Enemy
from classes.player import Player

ASSETS    = os.path.join(os.path.dirname(__file__), '..', 'test-data1')
TILE_SIZE = 32

class Game:
    def __init__(self):
        pygame.init()
        pygame.display.set_caption('Level 1')
        self.screen  = pygame.display.set_mode((640, 480))
        self.display = pygame.Surface((320, 240))
        self.clock   = pygame.time.Clock()

        tiles_path = os.path.join(ASSETS, 'images', 'tiles-objects', '1 Tiles')
        self.assets = {
            'tile':          load_images(tiles_path),
            'player/idle':   Animation(load_images(os.path.join(ASSETS, 'player', 'idle')),   6, scale=0.5),
            'player/run':    Animation(load_images(os.path.join(ASSETS, 'player', 'run')),    4, scale=0.5),
            'player/attack': Animation(load_images(os.path.join(ASSETS, 'player', 'attack')), 4, loop=False, scale=0.5),
            'player/death':  Animation(load_images(os.path.join(ASSETS, 'player', 'death')),  8, loop=False, scale=0.5),
            'enemy/idle':    Animation(load_images(os.path.join(ASSETS, 'enemies', 'idle')),    8),
            'enemy/walking': Animation(load_images(os.path.join(ASSETS, 'enemies', 'walking')), 6),
            'enemy/attack':  Animation(load_images(os.path.join(ASSETS, 'enemies', 'attack')),  4, loop=False),
            'enemy/death':   Animation(load_images(os.path.join(ASSETS, 'enemies', 'death')),   8, loop=False),
        }
        self.background = pygame.transform.scale(
            pygame.image.load(
                os.path.join(ASSETS, 'images', 'tiles-objects', '2 Background', 'pre.png')
            ).convert(),
            self.display.get_size()
        )

        # --- level layout (tile coords, tile_size=32) ---
        # y=7: ground spanning the full level width
        # y=5: first platform (reachable in one jump)
        # y=3: second platform (reachable from platform 1)
        self.tilemap = Tilemap(TILE_SIZE, ['tile'])
        for x in range(20):
            self.tilemap.place_tile_ongrid((x, 7), 'tile', 0)
        for x in range(3, 7):
            self.tilemap.place_tile_ongrid((x, 5), 'tile', 0)
        for x in range(11, 15):
            self.tilemap.place_tile_ongrid((x, 3), 'tile', 0)

        # player: hitbox 48×64, scaled sprite 64×64
        self.player = Player(self, (48, 3 * TILE_SIZE), (48, 64))

        # enemy on platform 2 (x=12 tile), placed so its bottom aligns with tile top
        self.enemies = [Enemy(self, (12 * TILE_SIZE, 3 * TILE_SIZE - 48), (32, 48))]

        self.scroll   = [0.0, 0.0]
        self.movement = [False, False]  # [left, right]

    def run(self):
        while True:
            self.display.fill((0, 0, 0))
            #self.display.blit(self.background, (0, 0))

            self.scroll[0] += (self.player.rect().centerx - self.display.get_width()  / 2 - self.scroll[0]) / 10
            self.scroll[1] += (self.player.rect().centery - self.display.get_height() / 2 - self.scroll[1]) / 10
            render_scroll = (int(self.scroll[0]), int(self.scroll[1]))

            self.tilemap.render(self.display, self.assets, offset=render_scroll)

            move_x = self.movement[1] - self.movement[0]
            self.player.update(self.tilemap, (move_x, 0), self.enemies)
            self.player.render(self.display, offset=render_scroll)

            for enemy in self.enemies:
                enemy.update(self.tilemap, self.player)
                enemy.render(self.display, offset=render_scroll)
            self.enemies = [e for e in self.enemies if not e.death_complete]

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_LEFT:
                        self.movement[0] = True
                    if event.key == pygame.K_RIGHT:
                        self.movement[1] = True
                    if event.key == pygame.K_UP and self.player.grounded and not self.player.dead:
                        self.player.physics.jump(self.player.velocity, 5)
                        self.player._ground_frames = 0
                    if event.key == pygame.K_x and not self.player.dead:
                        self.player.attack()
                if event.type == pygame.KEYUP:
                    if event.key == pygame.K_LEFT:
                        self.movement[0] = False
                    if event.key == pygame.K_RIGHT:
                        self.movement[1] = False

            self.screen.blit(pygame.transform.scale(self.display, self.screen.get_size()), (0, 0))
            pygame.display.update()
            self.clock.tick(60)


if __name__ == '__main__':
    Game().run()
