"""Unit tests for pygame_updater.tilemaps (Tilemap and Tile)."""
import pygame
import pytest

from pygame_updater.tilemaps.tile import Tile
from pygame_updater.tilemaps.tilemap import Tilemap


def test_tile_stores_attributes():
    tile = Tile("grass", (1, 2), 3, rotation=90)
    assert (tile.type, tile.position, tile.variant, tile.rotation) == ("grass", (1, 2), 3, 90)


def test_tile_rotation_defaults_to_zero():
    assert Tile("grass", (0, 0), 0).rotation == 0


def test_place_and_get_tile_ongrid():
    tm = Tilemap(tile_size=16)
    tm.place_tile_ongrid((2, 3), "wall", variant=1)
    tile = tm.get_tile((2, 3))
    assert tile.type == "wall"
    assert tile.variant == 1
    assert tile.position == (2, 3)


def test_remove_tile_clears_occupancy():
    tm = Tilemap(tile_size=16)
    tm.place_tile_ongrid((2, 3), "wall")
    tm.remove_tile((2, 3))
    assert tm.is_occupied_tile((2 * 16, 3 * 16)) is False


def test_get_missing_tile_raises():
    with pytest.raises(KeyError):
        Tilemap().get_tile((9, 9))


def test_is_occupied_tile_uses_pixel_coordinates():
    tm = Tilemap(tile_size=16)
    tm.place_tile_ongrid((2, 3), "wall")
    # any pixel inside tile (2, 3) -> occupied.
    assert tm.is_occupied_tile((33, 49)) is True
    assert tm.is_occupied_tile((47, 63)) is True


def test_is_occupied_tile_empty_cell():
    assert Tilemap(tile_size=16).is_occupied_tile((0, 0)) is False


def test_physics_rects_around_returns_collider_rect():
    tm = Tilemap(tile_size=16, colliding_tiles=["wall"])
    tm.place_tile_ongrid((1, 1), "wall")
    rects = tm.physics_rects_around((16, 16))
    assert pygame.Rect(16, 16, 16, 16) in rects


def test_physics_rects_around_skips_non_colliding_types():
    tm = Tilemap(tile_size=16, colliding_tiles=["wall"])
    tm.place_tile_ongrid((1, 1), "decoration")
    assert tm.physics_rects_around((16, 16)) == []


def test_physics_rects_around_empty_when_nothing_nearby():
    tm = Tilemap(tile_size=16, colliding_tiles=["wall"])
    tm.place_tile_ongrid((1, 1), "wall")
    assert tm.physics_rects_around((500, 500)) == []
