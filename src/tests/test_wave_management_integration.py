# src/tests/test_wave_management_integration.py

import pytest
from unittest.mock import MagicMock, patch
from src.views.game_view import NeododgeGame
from src.mechanics.wave_management.wave_manager import WaveManager


def test_wave_management_integration():
    """Test the integration of wave management components."""
    game_view = NeododgeGame()
    game_view.enemies = []
    game_view.all_sprites = []
    game_view.player = MagicMock()
    game_view.get_screen_dimensions = MagicMock(return_value=(800, 600))
    game_view.spawn_enemy = MagicMock()

    with patch('src.entities.enemies.chaser.Chaser'), \
         patch('src.entities.enemies.wanderer.Wanderer'):

        wave_generator = MagicMock()
        wave_generator.generate_wave.return_value = {
            "wave_number": 1,
            "type": "basic",
            "formation": "line",
            "enemy_count": 1,
            "orb_count": 0,
            "enemy_type": "basic"
        }

        wave_manager = WaveManager(wave_generator, game_view.spawn_enemy)
        wave_manager.game_view = game_view

        wave_manager.start_wave()

        assert game_view.spawn_enemy.call_count == 1
