import pygame
import os

def load_image(path: str, colorkey = (0,0,0)):
    image =  pygame.image.load(path).convert()
    image.set_colorkey(colorkey)
    return image

def load_images(path: str):
    images = []
    for image_name in sorted(os.listdir(path)):
        image = load_image(path + '/' + image_name)
        images.append(image)
    return images

class Animation:
    def __init__(self, images, image_dur, loop = True, scale = 1):
        self.images = images
        self.loop = loop
        self.image_duration = image_dur
        self.done = False
        self.frame = 0
        self.pause = False
        self.reset = False
        self.scale = scale
        self.backwards = False

    def update_frame(self):
        last_frame = self.image_duration * len(self.images) - 1

        if self.reset:
            self.frame = 0
            self.reset = False

        elif not self.done and not self.pause:
            if self.loop:
                if self.backwards:
                    self.frame = (self.frame - 1) % (self.image_duration * len(self.images))
                else:
                    self.frame = (self.frame + 1) % (self.image_duration * len(self.images))
            else:
                if self.backwards:
                    self.frame = max(self.frame - 1, 0)
                    if self.frame == 0:
                        self.done = True
                else:
                    self.frame = min(self.frame + 1, last_frame)
                    if self.frame == self.image_duration * len(self.images) - 1:
                        self.done = True


    def copy(self):
        return Animation(self.images, self.image_duration, self.loop)
    
    def anim_image(self):
        image =  self.images[int(self.frame / self.image_duration)]
        return pygame.transform.scale(image, (image.get_width() * self.scale, image.get_height() * self.scale))
    
    def is_finished(self):
        return self.done

    def pause_animation(self):
        self.pause = True

    def resume_animation(self):
        self.pause = False

    def reset_animation(self):
        self.reset = True

    def set_backwards(self):
        self.frame = len(self.images) * self.image_duration - 1
        self.backwards = True



