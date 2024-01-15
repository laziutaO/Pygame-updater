class Tilemap:
    def __init__(self, game, tile_size = 16, scale = 1):
        self.__tile_size = tile_size
        self.__tilemap = {}
        self.__scale = scale
        self.__tile_size = tile_size
        self.game = game
        self._offgrid_tiles = [{'type' : 'grass', 'pos' : (3, 10), 'variant': 1}]

        for i in range(10):
            self.__tilemap[str(3 + i) + ';10'] = {'type' : 'grass', 'pos' : (3 + i, 10), 'variant': 1}
            self.__tilemap['10;' + str(5 + i)] = {'type' : 'stone', 'pos' : (10, 5 + i), 'variant': 1}  

    def render(self, surf, offset = (0,0)):
        for tile in self._offgrid_tiles:
            surf.blit(self.game.assets[tile['type']][tile['variant']], tile['pos'])

        for loc in self.__tilemap:
            tile = self.__tilemap[loc]
            surf.blit(self.game.assets[tile['type']][tile['variant']], (tile['pos'][0] * self.__tile_size, tile['pos'][1] * self.__tile_size))

        