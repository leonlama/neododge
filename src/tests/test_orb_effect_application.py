import pytest
from unittest.mock import MagicMock
from src.views.game.orb_logic import apply_orb_effect_to_player

@pytest.mark.parametrize("orb_type,expected_effect", [
    ("slow", "slow"),
    ("speed_10", "speed"),
    ("speed_20", "speed"),
    ("mult_1.5x", "mult"),
    ("mult_2x", "mult"),
    ("cooldown_25", "cooldown"),
    ("cooldown_50", "cooldown"),
    ("shield", "shield"),
    ("vision", "vision"),
    ("hitbox", "hitbox"),
])
def test_apply_orb_effect_adds_correct_status_effect(orb_type, expected_effect):
    # Arrange
    player = MagicMock()
    player.status_effects = MagicMock()
    orb = MagicMock()
    orb.orb_type = orb_type

    # Act
    apply_orb_effect_to_player(player, orb)

    # Assert
    player.status_effects.add_effect.assert_called_once_with(expected_effect, duration=10)
