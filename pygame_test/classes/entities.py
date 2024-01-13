import pygame


class PhysicsEntity:
    def __init__(self, game, e_type, pos, size):
        self.game = game
        self.type = e_type
        self.pos = list(pos)
        self.size = size
        self.velocity = [0, 0]
        self.action = ''
        self.anim_offset = (-3, -3)
        self.flip = False
        self.set_action('idle')

    def set_action(self, action):
        if action != self.action:
            self.action = action
            self.animation = self.game.assets[self.type + '/' + self.action].copy()
            #self.animation.set_backwards()

    def update(self, tilemap, movement = (0,0)):
        frame_movement = (movement[0] + self.velocity[0], movement[1] + self.velocity[1])
        
        self.pos[0] += frame_movement[0]
        self.pos[1] += frame_movement[1]

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
        #surf.blit(self.game.assets['player'], self.pos)

class Player(PhysicsEntity):
    def __init__(self, game, pos, size):
        super().__init__(game, 'player', pos, size)

    def update(self, movement=(0,0), tilemap = None):
        super().update(tilemap, movement = movement)

        if movement[0] != 0:
            self.set_action('run')
        else:
            self.set_action('idle')

        