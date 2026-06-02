import pygame
import os


def load_image(path: str, colorkey=(0, 0, 0)):
    image = pygame.image.load(path).convert()
    image.set_colorkey(colorkey)
    return image


def load_images(path: str, colorkey=(0, 0, 0)):
    images = []
    for image_name in sorted(os.listdir(path)):
        image = load_image(path + '/' + image_name, colorkey)
        images.append(image)
    return images


class Animation:
    def __init__(self,
                 images: list,
                 image_duration: float,
                 loop=True,
                 scale=1):
        
        self.__images = images
        self.__loop = loop
        self.__image_duration = image_duration
        self.__scale = scale

        self.__frame_index = 0
        self.__elapsed_time = 0.0

        self.__done = False
        self.__pause = False
        self.__reset = False
        self.__backwards = False
        self.__callbacks = {}

    def update_frame(self, dt: float):

        if self.__reset:
            self.__frame_index = 0
            self.__elapsed_time = 0.0
            self.__done = False
            self.__reset = False
            return

        if self.__done or self.__pause:
            return

        self.__elapsed_time += dt

        while self.__elapsed_time >= self.__image_duration:
            self.__elapsed_time -= self.__image_duration

            if self.__loop:
                if self.__backwards:
                    self.__frame_index = (
                        self.__frame_index - 1
                    ) % len(self.__images)
                else:
                    self.__frame_index = (
                        self.__frame_index + 1
                    ) % len(self.__images)

            else:
                if self.__backwards:
                    self.__frame_index = max(
                        self.__frame_index - 1,
                        0
                    )

                    if self.__frame_index == 0:
                        self.__done = True

                else:
                    self.__frame_index = min(
                        self.__frame_index + 1,
                        len(self.__images) - 1
                    )

                    if self.__frame_index == len(self.__images) - 1:
                        self.__done = True

            if self.__frame_index in self.__callbacks:
                self.__callbacks[self.__frame_index]()

    def copy(self):
        return Animation(
            self.__images,
            self.__image_duration,
            self.__loop,
            self.__scale
        )

    def anim_image(self):
        image = self.__images[self.__frame_index]
        return pygame.transform.scale(image,(int(image.get_width() * self.__scale),
                                             int(image.get_height() * self.__scale)))

    def pause_animation(self):
        self.__pause = True

    def resume_animation(self):
        self.__pause = False

    def reset_animation(self):
        self.__reset = True

    def set_backwards(self):
        self.__frame_index = len(self.__images) - 1
        self.__backwards = True

    def add_callback_func(self, frame: int, func: callable):
        if callable(func):
            self.__callbacks[frame] = func
        else:
            raise Exception(
                "The provided function is not valid "
                "to be used as a callback function."
            )

    def is_finished(self):
        return self.__done

    def is_paused(self):
        return self.__pause

    def is_backwards(self):
        return self.__backwards

    def is_running(self):
        return not self.__done and not self.__pause

    def get_frame(self):
        return self.__frame_index