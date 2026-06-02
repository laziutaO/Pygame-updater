import math
import pytest

from pygame_updater.ai.search.astar import (
    AStar,
    GridGraph,
    astar,
    euclidean,
    manhattan,
    reconstruct_path,
)

def test_euclidean_distance():
    assert euclidean((0, 0), (3, 4)) == pytest.approx(5.0)

def test_manhattan_distance():
    assert manhattan((0, 0), (3, 4)) == 7

def test_reconstruct_path_walks_chain_to_root():
    came_from = {"A": None, "B": "A", "C": "B"}
    assert reconstruct_path(came_from, "C") == ["A", "B", "C"]



def test_astar_finds_path_endpoints(grid):
    path = astar(grid(["...", "...", "..."]), (0, 0), (2, 2))
    assert path[0] == (0, 0)
    assert path[-1] == (2, 2)


def test_astar_prefers_diagonal_on_open_grid(grid):
    assert astar(grid(["...", "...", "..."]), (0, 0), (2, 2)) == [(0, 0), (1, 1), (2, 2)]


def test_astar_returns_none_when_walled_off(grid):
    graph = grid([".#.", ".#.", ".#."]) 
    assert astar(graph, (0, 0), (2, 0)) is None


def test_astar_start_equals_end(grid):
    assert astar(grid(["..."]), (0, 0), (0, 0)) == [(0, 0)]


def test_astar_accepts_list_coordinates(grid):
    path = astar(grid(["..."]), [0, 0], [2, 0])
    assert path[0] == (0, 0) and path[-1] == (2, 0)


def test_astar_search_delegates_to_function(grid):
    follower = AStar(grid(["...", "...", "..."]))
    assert follower.search((0, 0), (2, 2))[-1] == (2, 2)


def test_astar_get_next_position_advances_along_path(grid):
    follower = AStar(grid(["...", "...", "..."]))
    first = follower.get_next_position((0, 0), (2, 2))
    second = follower.get_next_position((0, 0), (2, 2))
    assert first == (0, 0)
    assert second == (1, 1)
    assert follower.finished is False


def test_astar_get_next_position_unreachable_returns_start_and_flags_finished(grid):
    graph = grid([".#.", ".#.", ".#."])
    follower = AStar(graph)
    assert follower.get_next_position((0, 0), (2, 0)) == (0, 0)
    assert follower.finished is True
