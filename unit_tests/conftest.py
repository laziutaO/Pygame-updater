import os
import sys
from pathlib import Path
import pytest

os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
os.environ.setdefault("SDL_AUDIODRIVER", "dummy")

PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))
ASSETS_DIR = PROJECT_ROOT / "test-data1"

from pygame_updater.ai.search.astar import GridGraph


@pytest.fixture(scope="session", autouse=True)
def _sdl_display():
    import pygame

    pygame.display.init()
    pygame.display.set_mode((64, 64))
    yield
    pygame.display.quit()
    pygame.quit()


@pytest.fixture(scope="session")
def assets_dir():
    return ASSETS_DIR


class FakeBody:
    def __init__(self, rect=None, shape="rect", center=None, radius=0.0,
                 points=None, velocity=(0.0, 0.0), mass=1.0):
        self.rect = rect
        self.shape = shape
        self.center = list(center) if center is not None else None
        self.radius = radius
        self.points = points
        self.velocity = list(velocity)
        self.mass = mass


@pytest.fixture
def make_body():
    return FakeBody


def grid_from_ascii(rows, allow_diagonal=True, entity_size=(1, 1), step=1):
    blocked = {
        (x, y)
        for y, row in enumerate(rows)
        for x, ch in enumerate(row)
        if ch == "#"
    }
    height = len(rows)
    width = max(len(row) for row in rows)

    def passable(cell):
        x, y = cell
        return 0 <= x < width and 0 <= y < height and (x, y) not in blocked

    return GridGraph(passable, allow_diagonal=allow_diagonal,
                     entity_size=entity_size, step=step)


@pytest.fixture
def grid():
    return grid_from_ascii


def blocked_from_ascii(rows):
    blocked = {
        (x, y)
        for y, row in enumerate(rows)
        for x, ch in enumerate(row)
        if ch == "#"
    }
    return lambda cell: (int(cell[0]), int(cell[1])) in blocked


@pytest.fixture
def blocked_fn():
    return blocked_from_ascii
