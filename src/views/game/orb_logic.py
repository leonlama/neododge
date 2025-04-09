import random
import arcade

def spawn_orb(self, x=None, y=None, orb_type=None):
        """
        Spawn an orb at the specified position.

        Args:
            x (float): X-coordinate for the orb
            y (float): Y-coordinate for the orb
            orb_type (str, optional): Type of orb to spawn. If None, a random type will be chosen.
        """
        if x is None or y is None:
            # Random position within the screen
            x = random.randint(50, self.window.width - 50)
            y = random.randint(50, self.window.height - 50)

        # If no orb type specified, choose randomly
        if orb_type is None:
            # Determine if it's a buff or debuff orb
            orb_category = random.choices(
                ["buff", "debuff"], 
                weights=[0.7, 0.3]  # 70% chance for buff, 30% for debuff
            )[0]

            # Choose a specific orb type based on category
            if orb_category == "buff":
                orb_types = ["speed", "shield", "multiplier", "cooldown"]
                orb_type = random.choice(orb_types)
            else:  # debuff
                orb_types = ["slow", "vision", "hitbox"]
                orb_type = random.choice(orb_types)

        # Create the appropriate orb based on type
        try:
            if orb_type in ["speed", "shield", "multiplier", "cooldown"]:
                from src.mechanics.orbs.buff_orbs import BuffOrb
                orb = BuffOrb(x, y, orb_type)
                print(f"🔮 Spawned a buff orb: {orb_type}!")
            elif orb_type in ["slow", "vision", "hitbox"]:
                from src.mechanics.orbs.debuff_orbs import DebuffOrb
                orb = DebuffOrb(x, y, orb_type)
                print(f"🔮 Spawned a debuff orb: {orb_type}!")
            else:
                # Default to a random buff orb if type is unknown
                from src.mechanics.orbs.buff_orbs import BuffOrb
                orb = BuffOrb(x, y)
                print(f"🔮 Spawned a default buff orb!")

            # Add the orb to the appropriate sprite lists
            if hasattr(self, 'orbs'):
                self.orbs.append(orb)
            if hasattr(self, 'all_sprites'):
                self.all_sprites.append(orb)

        except Exception as e:
            print(f"Error spawning orb: {e}")

def spawn_orbs(self, count, orb_types=None, min_distance_from_player=100):
        """
        Spawn multiple orbs based on wave configuration.

        Args:
            count (int): Number of orbs to spawn
            orb_types (dict, optional): Distribution of orb types (e.g., {'buff': 0.7, 'debuff': 0.3})
            min_distance_from_player (float): Minimum distance from player to spawn orbs
        """
        if count <= 0:
            return

        # Default orb type distribution if none provided
        if orb_types is None:
            orb_types = {'buff': 0.7, 'debuff': 0.3}

        # Spawn the specified number of orbs
        for _ in range(count):
            # Choose a random position
            margin = 50
            x = random.randint(margin, self.window.width - margin)
            y = random.randint(margin, self.window.height - margin)

            # Ensure minimum distance from player
            if hasattr(self, 'player'):
                player_pos = (self.player.center_x, self.player.center_y)
                orb_pos = (x, y)
                distance = ((player_pos[0] - orb_pos[0])**2 + (player_pos[1] - orb_pos[1])**2)**0.5

                # If too close to player, try again
                if distance < min_distance_from_player:
                    continue

            # Determine orb category (buff or debuff)
            orb_category = random.choices(
                list(orb_types.keys()),
                weights=list(orb_types.values())
            )[0]

            # Choose specific orb type based on category
            if orb_category == "buff":
                orb_type = random.choice(["speed", "shield", "multiplier", "cooldown"])
            else:  # debuff
                orb_type = random.choice(["slow", "vision", "hitbox"])

            # Spawn the orb
            self.spawn_orb(x, y, orb_type=orb_type)

def check_orb_collisions(self):
        """Check for collisions between player and orbs."""
        # Get collisions
        orb_hit_list = arcade.check_for_collision_with_list(self.player, self.orbs)

        # Handle each collision
        for orb in orb_hit_list:
            # Apply orb effect
            if orb.orb_type == "buff":
                # Apply buff effect
                buff_type = orb.buff_type if hasattr(orb, 'buff_type') else random.choice(["speed", "health", "damage"])
                buff_amount = orb.buff_amount if hasattr(orb, 'buff_amount') else 0.2  # 20% buff

                # Apply the buff
                self.apply_buff(buff_type, buff_amount)

                # Play buff sound
                self.play_buff_sound()

                # Show buff message
                self.show_message(f"+{int(buff_amount*100)}% {buff_type.capitalize()} Buff!")

            # Add pickup text notification
            pickup_msg = "Buff collected!" if orb.orb_type in ["speed", "shield", "multiplier", "cooldown"] else "Debuff collected!"
            self.add_pickup_text(pickup_msg, self.player.center_x, self.player.center_y)

            # Remove the orb
            orb.remove_from_sprite_lists()

            # Update analytics
            if hasattr(self, 'wave_manager') and hasattr(self.wave_manager, 'wave_analytics'):
                self.wave_manager.wave_analytics.update_wave_stat(self.wave_manager.wave, "orbs_collected", 1)

def apply_orb_effect(self, orb):
        """Apply an orb's effect to the player."""
        # Get orb type
        orb_type = getattr(orb, 'orb_type', "unknown")

        print(f"Applying orb effect: {orb_type}")

        # Initialize attributes if they don't exist
        if not hasattr(self.player, 'speed_multiplier'):
            self.player.speed_multiplier = 1.0

        if not hasattr(self.player, 'has_shield'):
            self.player.has_shield = False

        # Handle different orb types
        if orb_type == "speed":
            # Speed buff
            self.player.speed_multiplier = 1.5
            self.player.speed_boost_timer = 5.0  # 5 seconds
            print(f"Applied speed buff: {self.player.speed_multiplier}x for {self.player.speed_boost_timer}s")

        elif orb_type == "shield":
            # Shield buff
            self.player.has_shield = True
            self.player.shield_timer = 5.0  # 5 seconds
            print(f"Applied shield buff for {self.player.shield_timer}s")

        elif orb_type == "vision":
            # Vision buff (similar to invincibility)
            self.player.is_invincible = True
            self.player.invincibility_timer = 3.0  # 3 seconds
            print(f"Applied vision buff for {self.player.invincibility_timer}s")

        elif orb_type == "cooldown":
            # Cooldown buff
            if hasattr(self.player, 'dash_cooldown'):
                self.player.dash_cooldown = 0  # Reset dash cooldown
            print(f"Applied cooldown buff: Dash ready!")

        elif orb_type == "multiplier":
            # Score multiplier buff
            if not hasattr(self.player, 'score_multiplier'):
                self.player.score_multiplier = 1.0
            self.player.score_multiplier = 2.0
            self.player.multiplier_timer = 10.0  # 10 seconds
            print(f"Applied score multiplier: {self.player.score_multiplier}x for {self.player.multiplier_timer}s")

        elif orb_type == "slow":
            # Slow debuff
            self.player.speed_multiplier = 0.85
            self.player.slow_timer = 4.0  # 4 seconds
            print(f"Applied slow debuff: {self.player.speed_multiplier}x for {self.player.slow_timer}s")

        elif orb_type == "hitbox":
            # Hitbox debuff (similar to damage)
            if hasattr(self.player, 'take_damage'):
                self.player.take_damage()
            print(f"Applied hitbox debuff: -1 health")

        # Update buff display
        self.update_buff_display()