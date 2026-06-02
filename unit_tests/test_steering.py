"""Unit tests for pygame_updater.ai.steering (Seek and Wander)."""
import math
import random

import pytest

from pygame_updater.ai.steering.seek import Seek
from pygame_updater.ai.steering.wander import Wander


# ---------- Seek ----------

def test_seek_drives_toward_target_at_max_speed():
    assert Seek(max_speed=2.0).velocity((0, 0), (10, 0)) == pytest.approx((2.0, 0.0))

def test_seek_decelerates_inside_slow_radius():
    # halfway into the slow radius -> half max speed.
    vx, vy = Seek(max_speed=2.0, slow_radius=10.0).velocity((0, 0), (5, 0))
    assert (vx, vy) == pytest.approx((1.0, 0.0))


def test_seek_full_speed_outside_slow_radius():
    speed = math.hypot(*Seek(max_speed=3.0, slow_radius=2.0).velocity((0, 0), (10, 0)))
    assert speed == pytest.approx(3.0)


def test_wander_velocity_has_max_speed_magnitude():
    random.seed(0)
    speed = math.hypot(*Wander(max_speed=2.5).velocity((0, 0)))
    assert speed == pytest.approx(2.5)


def test_wander_handles_zero_heading():
    random.seed(1)
    speed = math.hypot(*Wander(max_speed=2.0).velocity((0, 0), heading=(0, 0)))
    assert speed == pytest.approx(2.0)


def test_wander_angle_changes_within_jitter_bounds():
    random.seed(2)
    w = Wander(jitter=0.2)
    before = w._wander_angle
    w.velocity((0, 0))
    assert abs(w._wander_angle - before) <= 0.2
