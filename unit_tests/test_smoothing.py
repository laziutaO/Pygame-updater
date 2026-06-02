"""Unit tests for pygame_updater.ai.utils.smoothing.smooth_path."""
from pygame_updater.ai.utils.smoothing import smooth_path


def _clear(_cell):
    return False


def test_empty_path_returns_empty_list():
    assert smooth_path([], _clear) == []


def test_short_path_returned_as_copy():
    path = [(0, 0), (1, 1)]
    result = smooth_path(path, _clear)
    assert result == path
    assert result is not path


def test_collinear_clear_path_collapses_to_endpoints():
    path = [(0, 0), (1, 0), (2, 0), (3, 0)]
    assert smooth_path(path, _clear) == [(0, 0), (3, 0)]


def test_corner_is_kept_when_direct_line_is_blocked(blocked_fn):
    path = [(0, 0), (1, 1), (2, 0)]
    blocked = blocked_fn([".#."])
    assert smooth_path(path, blocked) == [(0, 0), (1, 1), (2, 0)]
