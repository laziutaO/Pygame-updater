"""Unit tests for pygame_updater.colliders.collisions."""
import math

import pygame
import pytest

from pygame_updater.colliders.collisions import (
    Collision,
    CollisionSystem,
    ComplexCollision,
)

SQUARE = [(0, 0), (10, 0), (10, 10), (0, 10)]


@pytest.fixture
def cc():
    return ComplexCollision()


def test_collide_circles_overlapping(cc):
    assert cc.collide_circles((0, 0), 1.0, (1, 0), 1.0) is True


def test_collide_circles_apart(cc):
    assert cc.collide_circles((0, 0), 1.0, (5, 0), 1.0) is False


def test_point_collide_poly_inside(cc):
    assert cc.point_collide_poly(SQUARE, (5, 5)) is True


def test_point_collide_poly_outside(cc):
    assert cc.point_collide_poly(SQUARE, (15, 15)) is False


def test_rect_collide_circle_center_inside_rect(cc):
    assert cc.rect_collide_circle((5, 5), 1.0, pygame.Rect(0, 0, 10, 10)) is True


def test_rect_collide_circle_just_in_range(cc):
    assert cc.rect_collide_circle((15, 5), 6.0, pygame.Rect(0, 0, 10, 10)) is True


def test_rect_collide_circle_out_of_range(cc):
    assert cc.rect_collide_circle((50, 50), 5.0, pygame.Rect(0, 0, 10, 10)) is False


def test_rect_collide_poly_overlap(cc):
    assert cc.rect_collide_poly(SQUARE, pygame.Rect(5, 5, 10, 10)) is True


def test_rect_collide_poly_rect_fully_inside_poly(cc):
    assert cc.rect_collide_poly(SQUARE, pygame.Rect(2, 2, 3, 3)) is True


def test_rect_collide_poly_separated(cc):
    assert cc.rect_collide_poly(SQUARE, pygame.Rect(50, 50, 5, 5)) is False


def test_broad_phase_reports_overlapping_pairs(make_body):
    a = make_body(rect=pygame.Rect(0, 0, 10, 10))
    b = make_body(rect=pygame.Rect(5, 5, 10, 10))
    assert CollisionSystem.broad_phase([a, b]) == [(a, b)]

'''
def test_broad_phase_ignores_disjoint_bodies(make_body):
    a = make_body(rect=pygame.Rect(0, 0, 10, 10))
    b = make_body(rect=pygame.Rect(50, 50, 10, 10))
    assert CollisionSystem.broad_phase([a, b]) == []'''

'''
def test_narrow_phase_rect_rect_normal_and_penetration(make_body):
    a = make_body(rect=pygame.Rect(0, 0, 10, 10))
    b = make_body(rect=pygame.Rect(8, 0, 10, 10))
    col = CollisionSystem().narrow_phase(a, b)
    assert col is not None
    assert col.normal == (1.0, 0.0)          # b is to the right of a
    assert col.penetration == pytest.approx(2.0)
'''

def test_narrow_phase_rect_rect_no_overlap_returns_none(make_body):
    a = make_body(rect=pygame.Rect(0, 0, 10, 10))
    b = make_body(rect=pygame.Rect(20, 0, 10, 10))
    assert CollisionSystem().narrow_phase(a, b) is None


def test_narrow_phase_circle_circle(make_body):
    a = make_body(shape="circle", center=(0, 0), radius=5,
                  rect=pygame.Rect(-5, -5, 10, 10))
    b = make_body(shape="circle", center=(8, 0), radius=5,
                  rect=pygame.Rect(3, -5, 10, 10))
    col = CollisionSystem().narrow_phase(a, b)
    assert col is not None
    assert col.normal == pytest.approx((1.0, 0.0))
    assert col.penetration == pytest.approx(2.0)


def test_narrow_phase_circle_rect(make_body):
    circle = make_body(shape="circle", center=(5, 12), radius=5,
                       rect=pygame.Rect(0, 7, 10, 10))
    rect = make_body(shape="rect", rect=pygame.Rect(0, 0, 10, 10))
    col = CollisionSystem().narrow_phase(circle, rect)
    assert col is not None
    assert math.hypot(*col.normal) == pytest.approx(1.0)
    assert col.penetration == pytest.approx(3.0)


def test_narrow_phase_unsupported_pair_degrades_to_aabb(make_body):
    a = make_body(shape="line", rect=pygame.Rect(0, 0, 10, 10))
    b = make_body(shape="line", rect=pygame.Rect(5, 5, 10, 10))
    col = CollisionSystem().narrow_phase(a, b)
    assert isinstance(col, Collision)


def test_resolve_separates_approaching_bodies(make_body):
    a = make_body(rect=pygame.Rect(0, 0, 10, 10), velocity=(1.0, 0.0), mass=1.0)
    b = make_body(rect=pygame.Rect(8, 0, 10, 10), velocity=(-1.0, 0.0), mass=1.0)
    system = CollisionSystem()
    system.resolve(system.narrow_phase(a, b))

    assert a.velocity[0] == pytest.approx(-1.0)
    assert b.velocity[0] == pytest.approx(1.0)



def test_step_fires_enter_then_exit_callbacks(make_body):
    system = CollisionSystem()
    events = []
    system.on_collision_enter(lambda a, b: events.append("enter"))
    system.on_collision_exit(lambda a, b: events.append("exit"))

    a = make_body(rect=pygame.Rect(0, 0, 10, 10))
    b = make_body(rect=pygame.Rect(5, 0, 10, 10))

    collisions = system.step([a, b])
    assert len(collisions) == 1
    assert events == ["enter"]

    # still overlapping next frame: no new enter, no exit.
    system.step([a, b])
    assert events == ["enter"]

    # pull them apart: exit fires once.
    b.rect = pygame.Rect(50, 0, 10, 10)
    assert system.step([a, b]) == []
    assert events == ["enter", "exit"]
