# src/tests/test_orb_spawner.py

import pytest
from unittest.mock import patch, MagicMock
from src.mechanics.wave_management.orb_spawner import spawn_orbs


class DummyScene:
    def add_sprite(self, name, sprite):
        pass


class DummyGameView:
    def __init__(self):
        self.scene = DummyScene()
        self.orbs = []
        self.width = 800
        self.height = 600
        self.get_screen_dimensions = lambda: (800, 600)


@patch('src.mechanics.wave_management.orb_spawner.get_random_orb')
def test_spawn_single_orb(mock_get_random_orb):
    dummy_orb = MagicMock()
    mock_get_random_orb.return_value = dummy_orb

    game_view = DummyGameView()
    spawn_orbs(game_view, count=1, orb_type_hint="speed")

    assert mock_get_random_orb.call_count == 1
    assert dummy_orb in game_view.orbs


@patch('src.mechanics.wave_management.orb_spawner.get_random_orb')
def test_spawn_multiple_orbs(mock_get_random_orb):
    dummy_orbs = [MagicMock() for _ in range(5)]
    mock_get_random_orb.side_effect = dummy_orbs

    game_view = DummyGameView()
    spawn_orbs(game_view, count=5, orb_type_hint="shield")

    assert mock_get_random_orb.call_count == 5
    assert all(orb in game_view.orbs for orb in dummy_orbs)


@patch('src.mechanics.wave_management.orb_spawner.get_random_orb')
def test_spawn_with_missing_scene(mock_get_random_orb):
    dummy_orbs = [MagicMock() for _ in range(2)]
    mock_get_random_orb.side_effect = dummy_orbs

    game_view = DummyGameView()
    del game_view.scene  # simulate scene being missing
    spawn_orbs(game_view, count=2, orb_type_hint="mult")

    assert mock_get_random_orb.call_count == 2
    assert all(orb in game_view.orbs for orb in dummy_orbs)
