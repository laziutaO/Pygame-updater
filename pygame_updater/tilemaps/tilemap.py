import pygame
NEIGHBOR_OFFSETS = [(0, -1), (1, 0), (0, 1), (-1, 0), (1, -1), (1, 1), (-1, 1), (-1, -1), (0, 0)]
PHYSICS_TILES = {'grass', 'stone'}

class Tilemap:
    def __init__(self, game, tile_size = 16, scale = 1):
        self.__tile_size = tile_size
        self.tilemap = {}
        self.__scale = scale
        self.game = game
        #self._offgrid_tiles = [{'type' : 'grass', 'pos' : (3, 10), 'variant': 1}]
        self.__offgrid_tiles = []

        for i in range(10):
            self.tilemap[str(3 + i) + ';10'] = {'type' : 'grass', 'pos' : (3 + i, 10), 'variant': 1}
            self.tilemap['10;' + str(5 + i)] = {'type' : 'stone', 'pos' : (10, 5 + i), 'variant': 1}  

    def render(self, surf):
        for tile in self.__offgrid_tiles:
            surf.blit(self.game.assets[tile['type']][tile['variant']], tile['pos'])

        for loc in self.tilemap:
            tile = self.tilemap[loc]
            surf.blit(self.game.assets[tile['type']][tile['variant']], (tile['pos'][0] * self.__tile_size, tile['pos'][1] * self.__tile_size))

    def tiles_around(self, pos):
        tiles = []
        tile_location = (int(pos[0] // self.__tile_size), int(pos[1] // self.__tile_size))
        for offset in NEIGHBOR_OFFSETS:
            check_location = str(tile_location[0] + offset[0]) + ';' + str(tile_location[1] + offset[1])
            if check_location in self.tilemap:
                tiles.append(self.tilemap[check_location])
        
        return tiles
    
    def physics_rects_around(self, pos):
        rects = []
        for tile in self.tiles_around(pos):
            if tile['type'] in PHYSICS_TILES:
                rects.append(pygame.Rect(tile['pos'][0] * self.__tile_size, tile['pos'][1] * self.__tile_size, self.__tile_size, self.__tile_size))
        return rects