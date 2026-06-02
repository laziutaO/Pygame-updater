"""Unit tests for pygame_updater.ai.navigation.flow_field.FlowField."""
import math

from pygame_updater.ai.navigation.flow_field import FlowField


def test_target_has_zero_cost_and_no_flow(grid):
    field = FlowField(grid(["...", "...", "..."]))
    field.build((1, 1))
    assert field.cost[(1, 1)] == 0.0
    assert field.direction((1, 1)) == (0.0, 0.0)


def test_direction_points_toward_target(grid):
    field = FlowField(grid(["...", "...", "..."]))
    field.build((0, 0))
    # the cell directly right of the target should steer back left to it.
    assert field.direction((1, 0)) == (-1.0, 0.0)


def test_flow_vectors_are_unit_length(grid):
    field = FlowField(grid(["....", "....", "....", "...."]))
    field.build((0, 0))
    for cell, vec in field.flow.items():
        if cell == (0, 0):
            continue
        assert math.isclose(math.hypot(*vec), 1.0)


def test_cost_increases_with_distance(grid):
    field = FlowField(grid(["....", "....", "....", "...."]))
    field.build((0, 0))
    assert field.cost[(3, 0)] > field.cost[(1, 0)] > field.cost[(0, 0)]

