import pygame
import pytest
from pygame_updater.animation.animations import Animation, load_image, load_images


def test_load_images_loads_every_frame(assets_dir):
    images = load_images(str(assets_dir / "player" / "idle"))
    assert len(images) == 6
    assert all(isinstance(img, pygame.Surface) for img in images)

def test_load_image_returns_surface(assets_dir):
    one = sorted((assets_dir / "player" / "idle").iterdir())[0]
    assert isinstance(load_image(str(one)), pygame.Surface)

@pytest.fixture
def frames():
    return [pygame.Surface((2, 2)) for _ in range(3)]

def test_animation_starts_on_first_frame(frames):
    assert Animation(frames, image_duration=0.1).get_frame() == 0

def test_update_frame(frames):
    anim = Animation(frames, image_duration=0.1)
    anim.update_frame(0.1)
    assert anim.get_frame() == 1

def test_looping_animation_wraps_around(frames):
    anim = Animation(frames, image_duration=0.1)

    for _ in range(6):
        anim.update_frame(0.1)

    assert anim.get_frame() == 0
    assert anim.is_finished() is False


def test_non_looping_animation_caps_and_finishes(frames):
    anim = Animation(frames, image_duration=0.1, loop=False)

    anim.update_frame(10.0)

    assert anim.get_frame() == len(frames) - 1
    assert anim.is_finished() is True

def test_pause_freezes_frame_then_resume_continues(frames):
    anim = Animation(frames, image_duration=0.1)
    anim.pause_animation()
    anim.update_frame(0.1)
    assert anim.get_frame() == 0
    assert anim.is_paused() is True
    anim.resume_animation()
    anim.update_frame(0.1)
    assert anim.get_frame() == 1


def test_reset_animation_returns_to_first_frame(frames):
    anim = Animation(frames, image_duration=0.1)

    anim.update_frame(0.2)

    anim.reset_animation()
    anim.update_frame(0.01)

    assert anim.get_frame() == 0


def test_frame_callback_fires_on_its_frame(frames):
    anim = Animation(frames, image_duration=0.1)

    hits = []

    anim.add_callback_func(
        1,
        lambda: hits.append(True)
    )

    anim.update_frame(0.1)

    assert hits == [True]

def test_add_callback_rejects_non_callable(frames):
    with pytest.raises(Exception):
        Animation(frames, image_duration=0.1).add_callback_func(0, 123)


def test_copy_is_independent_and_resets_frame(frames):
    anim = Animation(frames, image_duration=0.1)

    anim.update_frame(0.1)

    clone = anim.copy()

    assert clone.get_frame() == 0
    assert clone is not anim

def test_anim_image_applies_scale(frames):
    scaled = Animation(frames, image_duration=0.1, scale=2).anim_image()
    assert scaled.get_size() == (4, 4)

def test_is_running_reflects_pause_and_finish(frames):
    anim = Animation(frames, image_duration=0.1)
    assert anim.is_running() is True
    anim.pause_animation()
    assert anim.is_running() is False
