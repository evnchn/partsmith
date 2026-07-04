"""Shared fixtures: the spec (objective), the default part (candidate), and its params."""
import sys
import pathlib

import pytest

# make the project root importable when pytest is run from anywhere
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent.parent))

from atoms import spec as _spec  # noqa: E402
from parts import cable_clip  # noqa: E402


@pytest.fixture
def spec():
    return _spec.CABLE_CLIP


@pytest.fixture
def params():
    return dict(cable_clip.DEFAULT)


@pytest.fixture
def part(params):
    return cable_clip.make(params)
