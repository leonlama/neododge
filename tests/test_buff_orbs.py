import unittest
from scripts.orbs.buff_orbs import BuffOrb
from src.entities.player import Player

class TestBuffOrbs(unittest.TestCase):

    def setUp(self):
        self.player = Player(100, 100)
        self.player.pickup_messages = []

    def test_gray_orb_adds_heart_slot(self):
        orb = BuffOrb(100, 100, "gray")
        original_slots = self.player.max_slots
        orb.apply_effect(self.player)
        self.assertEqual(self.player.max_slots, original_slots + 1)

    def test_red_orb_heals_heart(self):
        self.player.max_slots = 3
        self.player.current_hearts = 1
        orb = BuffOrb(100, 100, "red")
        orb.apply_effect(self.player)
        self.assertEqual(self.player.current_hearts, 2)

    def test_gold_orb_adds_overheart(self):
        orb = BuffOrb(100, 100, "gold")
        orb.apply_effect(self.player)
        self.assertEqual(self.player.gold_hearts, 1)

    def test_speed_orbs_stack_bonus(self):
        orb10 = BuffOrb(100, 100, "speed_10")
        orb20 = BuffOrb(100, 100, "speed_20")
        orb30 = BuffOrb(100, 100, "speed_35")
        orb10.apply_effect(self.player)
        orb20.apply_effect(self.player)
        orb30.apply_effect(self.player)
        self.assertAlmostEqual(self.player.speed_bonus, 1.0 + 0.10 + 0.20 + 0.35)

    def test_mult_2_sets_multiplier(self):
        orb = BuffOrb(100, 100, "mult_2")
        orb.apply_effect(self.player)
        self.assertEqual(self.player.multiplier, 2.0)

    def test_mult_1_5_sets_multiplier(self):
        orb = BuffOrb(100, 100, "mult_1_5")
        orb.apply_effect(self.player)
        self.assertEqual(self.player.multiplier, 1.5)

    def test_shield_orb_gives_shield(self):
        orb = BuffOrb(100, 100, "shield")
        orb.apply_effect(self.player)
        self.assertTrue(self.player.shield)

    def test_cooldown_orb_reduces_cooldown(self):
        original_cooldown = self.player.cooldown
        orb = BuffOrb(100, 100, "cooldown")
        orb.apply_effect(self.player)
        self.assertLess(self.player.cooldown, original_cooldown)

