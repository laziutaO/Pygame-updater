import pygame
import os

def load_image(path: str, colorkey = (0,0,0)):
    image =  pygame.image.load(path).convert()
    image.set_colorkey(colorkey)
    return image

def load_images(path: str, colorkey = (0,0,0)):
    images = []
    for image_name in sorted(os.listdir(path)):
        image = load_image(path + '/' + image_name, colorkey)
        images.append(image)
    return images

class Animation:
    def __init__(self, images: list, image_dur: int, loop = True, scale = 1):
        self.__images = images
        self.__loop = loop
        self.__image_duration = image_dur
        self.__frame = 0
        self.__scale = scale
        self.__done = False
        self.__pause = False
        self.__reset = False
        self.__backwards = False
        self.__callbacks = {}

    def update_frame(self):
        last_frame = self.__image_duration * len(self.__images) - 1

        if self.__reset:
            self.__frame = 0
            self.__reset = False

        elif not self.__done and not self.__pause:
            if self.__loop:
                if self.__backwards:
                    self.__frame = (self.__frame - 1) % (self.__image_duration * len(self.__images))
                else:
                    self.__frame = (self.__frame + 1) % (self.__image_duration * len(self.__images))
            else:
                if self.__backwards:
                    self.__frame = max(self.__frame - 1, 0)
                    if self.__frame == 0:
                        self.__done = True
                else:
                    self.__frame = min(self.__frame + 1, last_frame)
                    if self.__frame == self.__image_duration * len(self.__images) - 1:
                        self.__done = True
            
            if self.__frame in self.__callbacks:
                self.__callbacks[self.__frame]()


    def copy(self):
        return Animation(self.__images, self.__image_duration, self.__loop)
    
    def anim_image(self):
        image =  self.__images[int(self.__frame / self.__image_duration)]
        return pygame.transform.scale(image, (image.get_width() * self.__scale, image.get_height() * self.__scale))

    def pause_animation(self):
        self.__pause = True

    def resume_animation(self):
        self.__pause = False

    def reset_animation(self):
        self.__reset = True

    def set_backwards(self):
        self.__frame = len(self.__images) * self.__image_duration - 1
        self.__backwards = True

    def add_callback_func(self, frame: int, func: callable):
        if callable(func):
            self.__callbacks[frame] = func
        else:
            raise Exception("The provided function is not valid to be used as a callback function.")
        
    def is_finished(self):
        return self.__done
    
    def is_paused(self):
        return self.__pause
    
    def is_backwards(self):
        return self.__backwards
    
    def is_running(self):
        return not self.__done and not self.__pause

    def get_frame(self):
        return self.__frame


