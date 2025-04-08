import unittest
from scripts.orbs.debuff_orbs import DebuffOrb
from src.entities.player import Player

class TestDebuffOrbs(unittest.TestCase):

    def setUp(self):
        self.player = Player(100, 100)

    def test_slow_reduces_speed(self):
        self.player.speed_bonus = 1.0
        orb = DebuffOrb(100, 100, "slow")
        orb.apply_effect(self.player)
        self.assertLess(self.player.speed_bonus, 1.0)

    def test_mult_down_halves_score(self):
        orb = DebuffOrb(100, 100, "mult_down_0_5")
        orb.apply_effect(self.player)
        self.assertEqual(self.player.multiplier, 0.5)

    def test_mult_down_quarters_score(self):
        orb = DebuffOrb(100, 100, "mult_down_0_25")
        orb.apply_effect(self.player)
        self.assertEqual(self.player.multiplier, 0.25)

    def test_cooldown_up_doubles_cooldown(self):
        orb = DebuffOrb(100, 100, "cooldown_up")
        orb.apply_effect(self.player)
        self.assertEqual(self.player.cooldown_factor, 2.0)

    def test_inverse_move_flag_set(self):
        orb = DebuffOrb(100, 100, "inverse_move")
        orb.apply_effect(self.player)
        self.assertTrue(self.player.inverse_move)

    def test_vision_blur_flag_set(self):
        orb = DebuffOrb(100, 100, "vision_blur")
        orb.apply_effect(self.player)
        self.assertTrue(self.player.vision_blur)

    def test_big_hitbox_increases_size(self):
        original_width = self.player.width
        original_height = self.player.height
        orb = DebuffOrb(100, 100, "big_hitbox")
        orb.apply_effect(self.player)
        self.assertGreater(self.player.width, original_width)
        self.assertGreater(self.player.height, original_height)

