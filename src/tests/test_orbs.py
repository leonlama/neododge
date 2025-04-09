import pytest
import arcade
from src.mechanics.orbs.buff_orbs import BuffOrb

def test_buff_orb_has_valid_type_and_texture(monkeypatch):
    # Mock die Textur-Funktion
    monkeypatch.setattr("arcade.Sprite.texture", arcade.make_soft_circle_texture(64, arcade.color.GREEN))
    orb = BuffOrb(100, 200, orb_type="speed")
    assert orb.orb_type == "speed"
