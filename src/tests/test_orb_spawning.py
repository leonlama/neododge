import pytest
import arcade
from unittest.mock import Mock
from src.views.game.orb_logic import check_orb_collisions
from src.views.game.spawn_logic import spawn_orbs
from src.mechanics.orbs.orb import Orb


class DummyOrb(Orb):
    def __init__(self):
        super().__init__(orb_type="test", x=100, y=100)
        self.collected = False

    def apply_effect(self, player):
        self.collected = True

    def kill(self):
        self.collected = True


def test_spawn_orbs_runs_without_crash():
    game_view = Mock()
    game_view.orb_spawn_timer = 1.0  # ✅ FIXED
    game_view.scene = {"orbs": arcade.SpriteList()}
    game_view.skin_manager = Mock()
    game_view.skin_manager.get_orb_texture.return_value = arcade.make_circle_texture(16, arcade.color.BLUE)
    game_view.get_spawn_position = lambda: (100, 100)
    game_view.wave_manager = Mock()
    game_view.wave_manager.wave = 1

    try:
        spawn_orbs(game_view)
    except Exception as e:
        pytest.fail(f"spawn_orbs raised an exception: {e}")


def test_check_orb_collisions_applies_effect():
    dummy_orb = DummyOrb()

    from src.entities.player.player import Player
    game_view = Mock()
    game_view.player = Player()
    game_view.player.texture = arcade.make_circle_texture(16, arcade.color.BLUE)

    game_view.orbs = arcade.SpriteList()
    game_view.orbs.append(dummy_orb)
    game_view.scene = {"orbs": game_view.orbs}
    game_view.wave_manager = Mock()
    game_view.wave_manager.wave = 1
    game_view.wave_manager.wave_analytics = Mock()

    # Ensure collision
    dummy_orb.center_x = game_view.player.center_x
    dummy_orb.center_y = game_view.player.center_y

    check_orb_collisions(game_view)

    assert dummy_orb.collected