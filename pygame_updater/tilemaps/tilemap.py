import pygame
import random
from tilemaps.tile import Tile
NEIGHBOR_OFFSETS = [(0, -1), (1, 0), (0, 1), (-1, 0), (1, -1), (1, 1), (-1, 1), (-1, -1), (0, 0)]

class Tilemap:
    def __init__(self, tile_size:int = 16, colliding_tiles: list = []):
        self.__tile_size = tile_size
        self.__tilemap = {}
        self.__offgrid_tiles = []
        self.__colliding_tiles = colliding_tiles

    def render(self, surf, tile_data: dict = {}, offset = (0,0)):
        for tile in self.__offgrid_tiles:
            surf.blit(pygame.transform.rotate(tile_data[tile.type][tile.variant], tile.rotation), (tile.position[0] - offset[0], tile.position[1] - offset[1]))

        for loc in self.__tilemap:
            tile = self.__tilemap[loc]
            surf.blit(pygame.transform.rotate(tile_data[tile.type][tile.variant], tile.rotation), (tile.position[0] * self.__tile_size - offset[0], tile.position[1] * self.__tile_size - offset[1]))

    def tiles_around(self, pos):
        tiles = []
        tile_location = (int(pos[0] // self.__tile_size), int(pos[1] // self.__tile_size))
        for offset in NEIGHBOR_OFFSETS:
            check_location = str(tile_location[0] + offset[0]) + ';' + str(tile_location[1] + offset[1])
            if check_location in self.__tilemap:
                tiles.append(self.__tilemap[check_location])
        
        return tiles
    
    def physics_rects_around(self, pos):
        rects = []
        for tile in self.tiles_around(pos):
            if tile.type in self.__colliding_tiles:
                rects.append(pygame.Rect(tile.position[0] * self.__tile_size, tile.position[1] * self.__tile_size, self.__tile_size, self.__tile_size))
        return rects
    
    def fill_tilemap(self, start: tuple, end: tuple, tile_type: str, variant = 0, rotation = 0):
        for x in range(start[0], end[0]):
            for y in range(start[1], end[1]):
                self.__tilemap[str(x) + ';' + str(y)] = Tile(tile_type, (x, y), variant, rotation)

    def fill_tilemap_random(self, start: tuple, end: tuple, tile_types: list, variants: list = [0]):
        for x in range(start[0], end[0]):
            for y in range(start[1], end[1]):
                self.__tilemap[str(x) + ';' + str(y)] = Tile(random.choice(tile_types), (x, y), random.choice(variants))

    def place_tile_offgrid(self, pos, tile_type, variant = 0, rotation = 0):
        self.__offgrid_tiles.append(Tile(tile_type, pos, variant, rotation))

    def place_tile_ongrid(self, pos, tile_type, variant =0, rotation = 0):
        self.__tilemap[str(pos[0]) + ';' + str(pos[1])] = Tile(tile_type, pos, variant, rotation)

    def remove_tile(self, pos: tuple):
        del self.__tilemap[str(pos[0]) + ';' + str(pos[1])]
    
    def get_tile(self, pos: tuple):
        return self.__tilemap[str(pos[0]) + ';' + str(pos[1])]

    def is_occupied_tile(self, pos):
        tile_location = (int(pos[0] // self.__tile_size), int(pos[1] // self.__tile_size))
        check_location = str(tile_location[0]) + ';' + str(tile_location[1])
        if(check_location in self.__tilemap):
            print("Tile is occupied")
        return check_location in self.__tilemap 

    



    