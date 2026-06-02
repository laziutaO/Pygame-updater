"""Unit tests for pygame_updater.physics.physics.PhysicsForces."""
import pytest

from pygame_updater.physics.physics import PhysicsForces


@pytest.fixture
def forces():
    return PhysicsForces()


def test_gravity_accelerates_downward_below_terminal(forces):
    assert forces.gravity([0.0, 0.0], 0.1, 5) == [0.0, 0.1]


def test_gravity_caps_at_terminal_velocity(forces):
    assert forces.gravity([0.0, 6.0], 0.1, 5) == [0.0, 5.0]


def test_gravity_honours_custom_direction(forces):
    assert forces.gravity([0.0, 0.0], 0.2, 10, direction=(1, 0)) == [0.2, 0.0]

def test_jump_applies_upward_impulse(forces):
    assert forces.jump([0.0, 0.0], 5) == [0.0, -5.0]


def test_apply_impulse_divides_by_mass(forces):
    assert forces.apply_impulse([0.0, 0.0], (10.0, 0.0), 2.0) == [5.0, 0.0]


def test_apply_force_uses_newtons_second_law(forces):
    assert forces.apply_force([0.0, 0.0], (10.0, 0.0), 2.0, dt=0.5) == [2.5, 0.0]


def test_apply_acceleration_scales_by_dt(forces):
    assert forces.apply_acceleration([1.0, 1.0], (2.0, 3.0), dt=2.0) == [5.0, 7.0]


def test_friction_snaps_to_zero_when_overshooting(forces):
    assert forces.friction([3.0, 4.0], 10.0) == [0.0, 0.0]


def test_friction_leaves_rest_untouched(forces):
    assert forces.friction([0.0, 0.0], 1.0) == [0.0, 0.0]


def test_drag_is_quadratic_in_speed(forces):
    # speed = 10, factor = 0.01 * 10 = 0.1, so vx -= 10 * 0.1 = 1.
    assert forces.drag([10.0, 0.0], 0.01) == pytest.approx([9.0, 0.0])

def test_clamp_speed_limits_magnitude_keeping_direction(forces):
    assert forces.clamp_speed([3.0, 4.0], 2.5) == pytest.approx([1.5, 2.0])


def test_knockback_pushes_away_from_source(forces):
    assert forces.knockback([0.0, 0.0], (0, 0), (3, 0), 2.0) == pytest.approx([2.0, 0.0])


def test_knockback_ignores_zero_distance(forces):
    assert forces.knockback([1.0, 1.0], (5, 5), (5, 5), 2.0) == [1.0, 1.0]


def test_bounce_reflects_into_surface(forces):
    # moving down (-y) into a floor with up normal reflects to +y.
    assert forces.bounce([0.0, -5.0], (0, 1), restitution=1.0) == pytest.approx([0.0, 5.0])


