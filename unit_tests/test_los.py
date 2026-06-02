"""Unit tests for pygame_updater.ai.utils.los.line_of_sight."""
from pygame_updater.ai.utils.los import line_of_sight


def test_clear_horizontal_line_is_visible(blocked_fn):
    assert line_of_sight((0, 0), (4, 0), blocked_fn(["....."])) is True


def test_blocked_cell_breaks_line(blocked_fn):
    assert line_of_sight((0, 0), (4, 0), blocked_fn([".._.."])) is True  # '_' is walkable
    assert line_of_sight((0, 0), (4, 0), blocked_fn(["..#.."])) is False


def test_clear_diagonal_line_is_visible(blocked_fn):
    grid = ["....", "....", "....", "...."]
    assert line_of_sight((0, 0), (3, 3), blocked_fn(grid)) is True


def test_blocked_endpoint_is_not_visible(blocked_fn):
    assert line_of_sight((0, 0), (2, 0), blocked_fn(["..#"])) is False
