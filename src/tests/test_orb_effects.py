from unittest.mock import MagicMock
import pytest
from src.views.game.orb_logic import apply_orb_effect_to_player

class DummyPlayer:
    def __init__(self):
        self.status_effects = MagicMock()

@pytest.mark.parametrize("orb_type,expected_effect", [
    ("speed_10", "speed"),
    ("speed_20", "speed"),
    ("mult_2x", "mult"),
    ("mult_1.5x", "mult"),
    ("cooldown_25", "cooldown"),
    ("cooldown_50", "cooldown"),
    ("shield", "shield"),
    ("vision", "vision"),
    ("hitbox", "hitbox"),
    ("slow", "slow"),
])
def test_apply_orb_effect_triggers_correct_status(orb_type, expected_effect):
    player = DummyPlayer()
    orb = MagicMock()
    orb.orb_type = orb_type

    apply_orb_effect_to_player(player, orb)

    # ✅ Verify that apply_status was called with correct effect type
    assert player.status_effects.apply_status.called, f"{orb_type} didn't call apply_status"
    called_args = player.status_effects.apply_status.call_args[0][0]
    assert expected_effect in called_args, f"Expected effect '{expected_effect}' not in '{called_args}'"

@pytest.mark.parametrize("orb_type,expected_method", [
    ("health", "heal"),
    ("gray_heart", "add_heart_slot"),
    ("gold_heart", "add_gold_heart"),
])
def test_healing_orbs_trigger_correct_player_method(orb_type, expected_method):
    player = MagicMock()
    orb = MagicMock()
    orb.orb_type = orb_type

    apply_orb_effect_to_player(player, orb)

    # ✅ Check the correct method was called
    method = getattr(player, expected_method)
    assert method.called, f"Expected {expected_method} to be called for orb type {orb_type}"
