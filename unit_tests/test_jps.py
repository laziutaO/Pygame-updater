"""Unit tests for pygame_updater.ai.search.jps."""
from pygame_updater.ai.search.jps import JPS, jps


def test_jps_path_connects_start_and_end(grid):
    path = jps(grid(["....." for _ in range(5)]), (0, 0), (4, 4))
    assert path is not None
    assert path[0] == (0, 0)
    assert path[-1] == (4, 4)


def test_jps_returns_none_when_start_blocked(grid):
    graph = grid(["#....", ".....", "....."])
    assert jps(graph, (0, 0), (4, 2)) is None


def test_jps_returns_none_when_end_blocked(grid):
    graph = grid([".....", ".....", "....#"])
    assert jps(graph, (0, 0), (4, 2)) is None


def test_jps_returns_none_when_walled_off(grid):
    graph = grid([".#.", ".#.", ".#."])
    assert jps(graph, (0, 0), (2, 0)) is None


def test_jps_class_delegates_to_function(grid):
    follower = JPS(grid(["....." for _ in range(5)]))
    assert follower.search((0, 0), (4, 4))[-1] == (4, 4)
