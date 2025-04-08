import random
import arcade
from src.core.constants import SCREEN_WIDTH, SCREEN_HEIGHT
from scripts.mechanics.orbs.buff_orbs import BuffOrb
from scripts.mechanics.orbs.debuff_orbs import DebuffOrb

class WaveManager:
    """Manages game waves and enemy spawning."""

    def __init__(self, game_view):
        self.game_view = game_view
        self.wave = 1
        self.wave_duration = 30.0  # seconds
        self.wave_pause = False
        self.wave_pause_timer = 0.0
        self.wave_message = ""
        self.wave_message_alpha = 0
        self.in_wave = True
        self.level_timer = 0.0

    def update(self, delta_time):
        """Update wave timers and state."""
        # Update level timer if not paused
        if not self.wave_pause:
            self.level_timer += delta_time

        # Update wave pause timer
        if self.wave_pause:
            self.wave_pause_timer -= delta_time
            if self.wave_pause_timer <= 0:
                self.wave_pause = False
                self.in_wave = True

        # Check for wave completion by time
        if self.in_wave and self.level_timer >= self.wave_duration:
            self.complete_wave()

    def complete_wave(self):
        """Handle wave completion."""
        self.in_wave = False
        self.wave_pause = True
        self.wave_pause_timer = 3.0
        self.wave += 1
        self.wave_message = f"Wave {self.wave} Complete!"
        self.wave_message_alpha = 255

        # Reset level timer
        self.level_timer = 0.0

    def start_next_wave(self, enemy_manager, enemy_list):
        """Start the next wave."""
        # Spawn enemies for the wave
        enemy_manager.spawn_enemies(enemy_list, self.wave, SCREEN_WIDTH, SCREEN_HEIGHT)
        
    def spawn_orbs(self, orb_list, count, screen_width, screen_height):
        """Spawn orbs based on frequency and wave number."""
        import random
        from scripts.mechanics.orbs.buff_orbs import BuffOrb
        from scripts.mechanics.orbs.debuff_orbs import DebuffOrb
        
        orb_info = []
        
        # Spawn 'count' number of orbs
        for _ in range(count):
            x = random.randint(50, screen_width - 50)
            y = random.randint(50, screen_height - 50)
            
            # Determine which orb to spawn based on frequencies
            orb_type = None
            
            # Speed orb (Common): Every 4-6 seconds
            if random.random() < 0.7:
                orb_type = "speed"
            
            # Shield orb (Uncommon): 10% chance per 10s
            elif random.random() < 0.1:
                orb_type = "shield"
            
            # Multiplier orb (Rare): 5% chance, every 15s, post Wave 5
            elif self.wave >= 5 and random.random() < 0.05:
                orb_type = "multiplier"
            
            # Cooldown orb (Common): Every 5-8s
            elif random.random() < 0.6:
                orb_type = "cooldown"
            
            # Vision Blur orb (Very Rare Debuff): From Wave 8+, 10% chance
            elif self.wave >= 8 and random.random() < 0.1:
                orb = DebuffOrb(x, y, "vision_blur")
                orb_list.append(orb)
                orb_info.append({"x": x, "y": y, "type": "vision_blur"})
                continue  # Skip to next iteration instead of returning
            
            # Default to speed orb if nothing was selected
            if orb_type is None:
                orb_type = "speed"
            
            # Create the selected orb
            orb = BuffOrb(x, y, orb_type)
            orb_list.append(orb)
            orb_info.append({"x": x, "y": y, "type": orb_type})
        
        return orb_info
