import pygame

BASE_IMG_PATH = 'test-data/images/'

def load_image(path):
    image =  pygame.image.load(BASE_IMG_PATH + path).convert()
    image.set_colorkey((0,0,0))
    return image