import pytest
from src.entities.player.player import Player

def test_take_damage_decreases_health():
    player = Player(100, 100)
    player.current_hearts = 3
    player.take_damage(1)
    assert player.current_hearts == 2
