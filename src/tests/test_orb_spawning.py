# src/tests/test_orb_spawning.py

import arcade
from unittest.mock import Mock
from src.views.game.orb_logic import check_orb_collisions


class DummyOrb(arcade.Sprite):
    def __init__(self):
        super().__init__()
        self.orb_type = "mult_2x"
        self.collected = False
        self.center_x = 100
        self.center_y = 100

    def collect(self):
        self.collected = True


def test_check_orb_collisions_applies_effect():
    dummy_orb = DummyOrb()

    from src.entities.player.player import Player
    game_view = Mock()
    game_view.player = Player()
    game_view.player.center_x = 100
    game_view.player.center_y = 100
    game_view.player.texture = arcade.make_circle_texture(16, arcade.color.BLUE)

    game_view.orbs = arcade.SpriteList()
    game_view.orbs.append(dummy_orb)
    game_view.scene = {"orbs": game_view.orbs}
    game_view.wave_manager = Mock()
    game_view.wave_manager.wave = 1
    game_view.wave_manager.wave_analytics = Mock()

    check_orb_collisions(game_view)

    assert dummy_orb.collected
