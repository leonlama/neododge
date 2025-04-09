import pytest
import time
from src.entities.player.status_effects import StatusEffectManager

class MockPlayer:
    def __init__(self):
        self.base_speed = 100
        self.base_cooldown = 1.0

def test_add_and_retrieve_single_effect():
    player = MockPlayer()
    manager = StatusEffectManager(player)
    manager.add_effect("speed", 5, {"value": +15})
    assert manager.get_total_value("speed") == 15

def test_stack_multiple_speed_effects():
    player = MockPlayer()
    manager = StatusEffectManager(player)
    manager.add_effect("speed", 5, {"value": +10})
    manager.add_effect("speed", 5, {"value": +5})
    assert manager.get_total_value("speed") == 15

def test_expired_effect_is_removed():
    player = MockPlayer()
    manager = StatusEffectManager(player)
    manager.add_effect("speed", 0.01, {"value": +20})
    time.sleep(0.02)
    manager.update(0.02)
    assert manager.get_total_value("speed") == 0