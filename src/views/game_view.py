import arcade
import random
from src.controllers.game_controller import GameController
from src.entities.player.player import Player
from src.core.constants import (
    SCREEN_WIDTH, 
    SCREEN_HEIGHT, 
    PLAYER_SCALE, 
    ARTIFACT_SCALE,
    WAVE_TEXT_DURATION,
    WAVE_DURATION
)
from src.skins.skin_manager import skin_manager
from src.audio.sound_manager import sound_manager

from src.mechanics.artifacts.dash_artifact import DashArtifact
from src.mechanics.coins.coin import Coin
from src.mechanics.orbs.orb_pool import get_random_orb
from src.views.shop_view import ShopView

from src.mechanics.wave_management.wave_manager import WaveManager
from src.controllers.game_controller import GameController
from src.ui.improved_hud import (
    draw_wave_info,
    draw_score,
    draw_player_health,
    draw_active_effects,
    draw_coin_count,
    draw_wave_message,
    draw_pickup_texts
)

from src.ui.pickup_text import PickupText
from src.views.game.update import update_game
from src.views.game.collision_logic import check_collisions, check_orb_collisions

class NeododgeGame(arcade.View):
    """Main game view."""

    def __init__(self):
        super().__init__()
        self.player = None
        self.enemies = arcade.SpriteList()
        self.orbs = arcade.SpriteList()
        self.coins = arcade.SpriteList()
        self.artifacts = arcade.SpriteList()
        self.game_controller = None
        self.score = 0
        self.pickup_texts = []
        self.buff_display_text = []

        # Mouse tracking
        self.mouse_x = 0
        self.mouse_y = 0
        self.right_mouse_down = False

        # Set up the camera
        self.camera = arcade.Camera(SCREEN_WIDTH, SCREEN_HEIGHT)

        # Set up the GUI camera
        self.gui_camera = arcade.Camera(SCREEN_WIDTH, SCREEN_HEIGHT)

    def spawn_enemy(self, enemy_type, position, speed=1.0, health=1.0):
        """Spawn an enemy with the given parameters."""
        print(f"Game view spawning enemy: {enemy_type} at {position} with speed={speed}, health={health}")

        # Extract position components
        if isinstance(position, tuple) and len(position) >= 2:
            x, y = position[0], position[1]
        else:
            print(f"Invalid position format: {position}")
            window = arcade.get_window()
            x, y = random.randint(50, window.width - 50), random.randint(50, window.height - 50)

        # Create enemy based on type
        enemy = None

        try:
            # Use the correct class names
            if enemy_type == "chaser":
                from src.entities.enemies.chaser import Chaser
                enemy = Chaser(x, y)
            elif enemy_type == "wander":
                from src.entities.enemies.wanderer import Wanderer
                enemy = Wanderer(x, y)
            elif enemy_type == "shooter":
                from src.entities.enemies.shooter import Shooter
                enemy = Shooter(x, y)
            elif enemy_type == "boss":
                from src.entities.enemies.boss import Boss
                enemy = Boss(x, y)
        except ImportError as e:
            print(f"Error importing enemy class: {e}")
            # Fall back to a basic enemy implementation
            try:
                # Create a basic enemy sprite
                enemy = arcade.Sprite()
                enemy.center_x = x
                enemy.center_y = y

                # Set appearance based on enemy type
                if enemy_type == "chaser":
                    enemy.texture = arcade.make_circle_texture(30, arcade.color.PURPLE)
                elif enemy_type == "wanderer":
                    enemy.texture = arcade.make_circle_texture(30, arcade.color.ORANGE)
                elif enemy_type == "shooter":
                    enemy.texture = arcade.make_circle_texture(30, arcade.color.BLUE)
                else:
                    enemy.texture = arcade.make_circle_texture(30, arcade.color.RED)

                # Set basic properties
                enemy.scale = 1.0
                enemy.speed = speed
                enemy.health = health
                enemy.enemy_type = enemy_type

                print(f"Created fallback enemy of type: {enemy_type}")
            except Exception as e:
                print(f"Error creating fallback enemy: {e}")
                return
        except Exception as e:
            print(f"Error creating enemy: {e}")
            return

        if enemy:
            # Apply speed and health modifiers
            if hasattr(enemy, 'speed'):
                enemy.speed *= speed
            if hasattr(enemy, 'max_health'):
                enemy.max_health = int(enemy.max_health * health)
                enemy.health = enemy.max_health

            # Add to sprite lists
            print(f"Adding enemy to sprite lists")
            self.enemies.append(enemy)

            # Add to scene if it exists
            if hasattr(self, 'scene') and hasattr(self.scene, 'add_sprite'):
                try:
                    self.scene.add_sprite("enemies", enemy)
                except Exception as e:
                    print(f"Error adding to scene: {e}")

            return enemy

    def spawn_artifact(self, x=None, y=None, artifact_type=None):
        """
        Spawn an artifact at the specified position or a random position.

        Args:
            x (float, optional): X-coordinate for the artifact. If None, a random position is chosen.
            y (float, optional): Y-coordinate for the artifact. If None, a random position is chosen.
            artifact_type (str, optional): Type of artifact to spawn. If None, a random type is chosen.

        Returns:
            bool: True if artifact was spawned successfully, False otherwise.
        """
        # Import the artifact class
        try:
            from src.mechanics.artifacts.base import Artifact
            from src.mechanics.artifacts.dash_artifact import DashArtifact
            from src.mechanics.artifacts.bullet_time import BulletTimeArtifact
            # Import other artifact types as needed
        except ImportError as e:
            print(f"Error importing artifact classes: {e}")
            return False

        # If no position specified, choose a random position
        if x is None or y is None:
            margin = 50
            max_attempts = 10  # Limit attempts to find valid position

            for _ in range(max_attempts):
                # Generate random position
                x = random.randint(margin, self.window.width - margin)
                y = random.randint(margin, self.window.height - margin)

                # Check distance from player
                if hasattr(self, 'player'):
                    player_pos = (self.player.center_x, self.player.center_y)
                    artifact_pos = (x, y)
                    distance = ((player_pos[0] - artifact_pos[0])**2 + (player_pos[1] - artifact_pos[1])**2)**0.5

                    # If too close to player, try again
                    if distance < 100:  # Minimum distance
                        continue

                # Valid position found
                break

        # If no artifact type specified, choose a random one
        if artifact_type is None:
            artifact_types = ["dash", "bullet_time"]  # Add more types as needed
            artifact_type = random.choice(artifact_types)

        try:
            # Create the appropriate artifact based on type
            if artifact_type == "dash":
                artifact = DashArtifact(x, y)
            elif artifact_type == "bullet_time":
                artifact = BulletTimeArtifact(x, y)
            else:
                print(f"Unknown artifact type: {artifact_type}")
                return False

            # Add to sprite lists
            if not hasattr(self, 'artifacts'):
                self.artifacts = arcade.SpriteList()

            self.artifacts.append(artifact)

            # Add to all_sprites if it exists
            if hasattr(self, 'all_sprites'):
                self.all_sprites.append(artifact)

            print(f"🔮 Spawned a {artifact_type} artifact at ({x}, {y})!")
            return True

        except Exception as e:
            print(f"Error spawning artifact: {e}")
            return False

    def clear_enemies(self):
        """Clear all enemies from the screen."""
        self.enemies = arcade.SpriteList()

    def on_wave_start(self, wave_config):
        """
        Called when a new wave starts.

        Args:
            wave_config (dict): The configuration for the new wave
        """
        wave_number = wave_config["wave_number"]
        wave_type = wave_config["type"]

        # Show appropriate message based on wave type
        if wave_type == "normal":
            self.show_message(f"Wave {wave_number}")
        elif wave_type == "swarm":
            self.show_message(f"Swarm Wave {wave_number}!")
        elif wave_type == "elite":
            self.show_message(f"Elite Wave {wave_number}!")
        elif wave_type == "boss":
            self.show_message(f"BOSS WAVE {wave_number}!")

        print(f"🌊 Starting {wave_type} wave {wave_number}")

    def on_wave_end(self, wave_number):
        """
        Called when a wave ends.

        Args:
            wave_number (int): The completed wave number
        """
        self.show_message(f"Wave {wave_number} Complete!")
        self.score += wave_number * 100  # Bonus points for completing a wave
        print(f"🌊 Wave {wave_number} completed! Score: {self.score}")
        
    def start_next_wave(self, delta_time=0):
        """Start the next wave."""
        self.wave_manager.start_wave()

    def setup_sounds(self):
        """Set up game sounds."""
        # We'll use the sound manager instead of loading sounds directly
        pass

    def play_coin_sound(self):
        """Play the coin pickup sound."""
        try:
            sound_manager.play_sound("coin", "collect")
        except Exception as e:
            print(f"Error playing coin sound: {e}")

    def play_damage_sound(self):
        """Play the damage sound."""
        # Check if player has damage sound cooldown
        if hasattr(self.player, 'damage_sound_cooldown') and self.player.damage_sound_cooldown:
            return

        try:
            # Always use the sound manager for consistent volume control
            sound_manager.play_sound("player", "damage")

            # Set cooldown
            self.player.damage_sound_cooldown = True

            # Reset cooldown after a short delay
            arcade.schedule(self.reset_damage_sound_cooldown, 0.5)
        except Exception as e:
            print(f"Error playing damage sound: {e}")

    def reset_damage_sound_cooldown(self, dt):
        """Reset the damage sound cooldown."""
        if hasattr(self.player, 'damage_sound_cooldown'):
            self.player.damage_sound_cooldown = False

    def play_buff_sound(self):
        """Play the buff pickup sound."""
        try:
            sound_manager.play_sound("orb", "buff")
        except Exception as e:
            print(f"Error playing buff sound: {e}")

    def play_debuff_sound(self):
        """Play the debuff pickup sound."""
        try:
            sound_manager.play_sound("orb", "debuff")
        except Exception as e:
            print(f"Error playing debuff sound: {e}")

    def on_show(self):
        """Called when this view becomes active"""
        arcade.set_background_color(arcade.color.BLACK)

    def on_draw(self):
        """Render the screen."""
        try:
            # Start rendering
            arcade.start_render()
            
            # Draw background
            if hasattr(self, 'background') and self.background:
                self.background.draw()
    
            # Use game camera for game elements
            self.camera.use()
    
            # Draw all sprites
            if hasattr(self, 'player') and self.player:
                self.player.draw()
    
            if hasattr(self, 'enemies'):
                self.enemies.draw()
    
            if hasattr(self, 'orbs'):
                self.orbs.draw()
    
            if hasattr(self, 'coins'):
                self.coins.draw()
    
            if hasattr(self, 'artifacts'):
                self.artifacts.draw()
    
            # Draw enemy bullets
            for enemy in self.enemies:
                if hasattr(enemy, 'bullets'):
                    enemy.bullets.draw()
    
            # Use GUI camera for UI elements
            self.gui_camera.use()
    
            # 💚 Top-left hearts
            from src.ui.improved_hud import draw_player_health
            if hasattr(self, 'player') and self.player:
                draw_player_health(self.player, self.heart_textures)
    
            # 💯 Score
            from src.ui.improved_hud import draw_score
            draw_score(self.score)
    
            # 💥 Top-right active effects
            from src.ui.improved_hud import draw_active_effects
            if hasattr(self, 'player') and self.player and hasattr(self.player, 'status_effects'):
                draw_active_effects(self.player.status_effects)
    
            # 💸 Coins bottom-right
            from src.ui.improved_hud import draw_coin_count
            if hasattr(self, 'player') and self.player:
                draw_coin_count(getattr(self.player, 'coins', 0))
    
            # 🌊 Top-center wave info
            from src.ui.improved_hud import draw_wave_info
            if hasattr(self, 'wave_manager'):
                draw_wave_info(
                    self.wave_manager.current_wave,
                    wave_timer=getattr(self.wave_manager, 'wave_timer', None),
                    enemies_left=len(self.enemies) if hasattr(self, 'enemies') else None
                )
    
            # Draw any pickup texts
            if hasattr(self, 'pickup_texts'):
                for text_obj in self.pickup_texts:
                    text_obj.draw()
    
            # Draw wave message if active
            if hasattr(self, 'wave_message') and hasattr(self, 'wave_message_alpha') and self.wave_message_alpha > 0:
                from src.ui.improved_hud import draw_wave_message
                draw_wave_message(self.wave_message, self.wave_message_alpha)
    
            # Draw message if active
            if hasattr(self, 'message') and hasattr(self, 'message_timer') and self.message_timer > 0:
                arcade.draw_text(
                    self.message,
                    self.window.width / 2,
                    self.window.height / 2,
                    arcade.color.WHITE,
                    font_size=24,
                    anchor_x="center",
                    anchor_y="center",
                    bold=True
                )
    
            # Draw debug info if enabled
            if hasattr(self, 'debug_mode') and self.debug_mode:
                self.draw_debug_info()
    
        except Exception as e:
            print("❌ Error in on_draw:", e)
            import traceback
            traceback.print_exc()
    
    def draw_buffs(self):
        """Draw active buffs on screen."""
        if not hasattr(self, 'buff_display_text'):
            self.buff_display_text = []

        # Draw each buff
        y = self.window.height - 80  # Start below health
        for buff_text in self.buff_display_text:
            arcade.draw_text(
                buff_text,
                10,
                y,
                arcade.color.YELLOW,
                font_size=14
            )
            y -= 20

    def draw_game_elements(self):
        """Draw all game elements."""
        # Activate the game camera
        self.camera.use()

        # Draw game elements
        self.enemies.draw()
        self.orbs.draw()
        self.coins.draw()
        self.artifacts.draw()

        # Draw player
        self.player.draw()

        # Draw enemy bullets
        for enemy in self.enemies:
            if hasattr(enemy, 'bullets'):
                enemy.bullets.draw()

        # Draw dash artifact if it exists
        if self.dash_artifact:
            self.dash_artifact.draw()

        # Activate the GUI camera for HUD elements
        self.gui_camera.use()
        
    def draw_improved_hud(self):
        """Draw the improved HUD."""
        from src.ui.improved_hud import draw_hud

        # Ensure heart textures exist
        if not hasattr(self, 'heart_textures') or not self.heart_textures.get('red') or not self.heart_textures.get('gray'):
            # Create fallback textures
            self.heart_textures = {
                "red": arcade.make_soft_circle_texture(30, arcade.color.RED),
                "gray": arcade.make_soft_circle_texture(30, arcade.color.GRAY)
            }

        # Get the current wave number
        wave_number = getattr(self.wave_manager, 'wave', 1)

        # Calculate the wave time left as a countdown
        wave_time_left = max(0, int(self.wave_manager.wave_duration - self.wave_manager.wave_timer))

        try:
            # Draw HUD
            draw_hud(
                self.player,
                self.score,
                wave_number,
                wave_time_left,
                self.heart_textures
            )
        except Exception as e:
            print(f"Error drawing HUD: {e}")
            # Fallback to simple HUD
            self.draw_simple_hud()

    def draw_simple_hud(self):
        """Draw a simple HUD as fallback."""
        # Draw score
        arcade.draw_text(
            f"Score: {int(self.score)}",
            20, 
            self.window.height - 40,
            arcade.color.WHITE,
            16
        )

        # Draw wave number
        if hasattr(self, 'wave_manager'):
            wave = getattr(self.wave_manager, 'wave', 1)
            arcade.draw_text(
                f"Wave: {wave}",
                self.window.width // 2,
                self.window.height - 40,
                arcade.color.WHITE,
                16,
                anchor_x="center"
            )

        # Draw health
        if hasattr(self, 'player'):
            hearts = getattr(self.player, 'current_hearts', 3)
            max_hearts = getattr(self.player, 'max_hearts', 3)

            arcade.draw_text(
                f"Health: {hearts}/{max_hearts}",
                self.window.width - 150,
                self.window.height - 40,
                arcade.color.WHITE,
                16
            )
    def add_effect(self, effect_type, duration=None, value=None, is_percentage=True, color=None, icon_name=None):
        """Adds an effect with full flexibility."""
        # Apply the effect to the player
        if hasattr(self.player, 'apply_effect'):
            self.player.apply_effect(effect_type, value, duration, is_percentage)

        # Add a visual indicator
        if hasattr(self, 'effect_indicators'):
            self.effect_indicators.append({
                'type': effect_type,
                'value': value,
                'duration': duration,
                'is_percentage': is_percentage,
                'color': color,
                'icon': icon_name
            })

    def add_pickup_text(self, text, x, y):
        """Add floating text for item pickups."""
        if not hasattr(self, 'pickup_texts'):
            self.pickup_texts = []

        # Add text with position and lifetime
        self.pickup_texts.append(PickupText(text, x, y))  # 1.0 second lifetime

    def update_enemies(self, delta_time):
        """Update all enemies and their bullets."""
        # Update each enemy
        for enemy in self.enemies:
            enemy.update(delta_time)

            # Handle enemy bullets
            if hasattr(enemy, 'bullets'):
                # Check for bullet-player collisions
                bullet_hit_list = arcade.check_for_collision_with_list(self.player, enemy.bullets)
                for bullet in bullet_hit_list:
                    # Remove the bullet
                    bullet.remove_from_sprite_lists()

                    # Player takes damage
                    if hasattr(self.player, 'take_damage'):
                        self.player.take_damage()

                        # Play damage sound
                        self.play_damage_sound()

                # Update bullets
                enemy.bullets.update()  # Remove delta_time parameter

                # If bullets need delta_time, update each bullet individually
                for bullet in enemy.bullets:
                    if hasattr(bullet, 'update_with_time'):
                        bullet.update_with_time(delta_time)

    def on_update(self, delta_time: float):
        update_game(delta_time, self)
        check_collisions(self)
        check_orb_collisions(self)
                
    def apply_buff(self, buff_type, amount):
        """Apply a buff to the player.

        Args:
            buff_type: Type of buff (speed, health, damage)
            amount: Amount to buff (0.2 = 20% increase)
        """
        print(f"Applying {buff_type} buff: +{amount*100:.0f}%")

        if buff_type == "speed":
            # Increase player speed
            self.player.speed_multiplier = self.player.speed_multiplier * (1 + amount)
            print(f"Player speed now: {self.player.speed_multiplier:.2f}x")

        elif buff_type == "health":
            # Increase player max health
            old_max = self.player.max_health
            self.player.max_health = int(self.player.max_health * (1 + amount))
            # Also heal the player by the amount gained
            health_gained = self.player.max_health - old_max
            self.player.health = min(self.player.max_health, self.player.health + health_gained)
            print(f"Player health now: {self.player.health}/{self.player.max_health}")

        elif buff_type == "damage":
            # Increase player damage
            if hasattr(self.player, 'damage_multiplier'):
                self.player.damage_multiplier = self.player.damage_multiplier * (1 + amount)
            else:
                self.player.damage_multiplier = 1 + amount
            print(f"Player damage now: {self.player.damage_multiplier:.2f}x")

        # Update UI to show new buff
        self.update_buff_display()
        
    def update_buff_display(self):
        """Update the buff display in the UI."""
        # Create buff text to display
        buff_text = []

        if hasattr(self.player, 'speed_boost_timer') and self.player.speed_boost_timer > 0:
            buff_text.append(f"Speed: +50% ({self.player.speed_boost_timer:.1f}s)")

        if hasattr(self.player, 'slow_timer') and self.player.slow_timer > 0:
            buff_text.append(f"Slow: -50% ({self.player.slow_timer:.1f}s)")

        if hasattr(self.player, 'shield_timer') and self.player.shield_timer > 0:
            buff_text.append(f"Shield: Active ({self.player.shield_timer:.1f}s)")

        if hasattr(self.player, 'invincibility_timer') and self.player.invincibility_timer > 0:
            buff_text.append(f"Invincible: ({self.player.invincibility_timer:.1f}s)")

        # Store buff text for drawing in on_draw
        self.buff_display_text = buff_text
        
    def check_collisions(self):
        """Check for collisions between game objects."""
        # Player-Enemy collisions
        if self.player and not getattr(self.player, 'invincible', False):
            enemy_hit_list = arcade.check_for_collision_with_list(self.player, self.enemies)
            for enemy in enemy_hit_list:
                # Handle player taking damage
                if hasattr(self.player, 'take_damage'):
                    damage = getattr(enemy, 'damage', 1)
                    self.player.take_damage(damage)
                    
                    # Play damage sound
                    self.play_damage_sound()

                # Remove enemy if it's a one-hit enemy
                if hasattr(enemy, 'is_one_hit') and enemy.is_one_hit:
                    enemy.remove_from_sprite_lists()

        # Player-Coin collisions
        coin_hit_list = arcade.check_for_collision_with_list(self.player, self.coins)
        for coin in coin_hit_list:
            # Remove the coin
            coin.remove_from_sprite_lists()

            # Handle coin collection
            if hasattr(self.player, 'collect_coin'):
                self.player.collect_coin()
            else:
                # Fallback if player doesn't have collect_coin method
                if hasattr(self.player, 'coins'):
                    self.player.coins += 1
                else:
                    self.player.coins = 1

                # Add to score
                self.score += 10

            # Play coin sound
            self.play_coin_sound()

            # Add pickup text
            if hasattr(self, 'add_pickup_text'):
                self.add_pickup_text("Coin collected!", self.player.center_x, self.player.center_y)

        # Player-Orb collisions
        for orb in list(self.orbs):  # Use a copy of the list to safely modify during iteration
            distance = ((self.player.center_x - orb.center_x) ** 2 + 
                        (self.player.center_y - orb.center_y) ** 2) ** 0.5
            
            # Check if player is close enough to collect the orb
            # Use a generous collision radius to make collection easier
            collision_radius = getattr(self.player, 'collision_radius', 30) + getattr(orb, 'collision_radius', 15)

            if distance <= collision_radius:
                print(f"Collision detected with {orb.orb_type} orb!")

                # Get orb type and message
                orb_type = getattr(orb, 'orb_type', "unknown")
                message = getattr(orb, 'message', "Orb collected!")

                # Apply the orb effect
                try:
                    self.apply_orb_effect(orb)
                    print(f"Applied orb effect: {orb_type}")

                    # Remove the orb
                    orb.remove_from_sprite_lists()

                    # Play appropriate sound
                    if orb_type in ["speed", "shield", "invincibility"]:
                        self.play_buff_sound()
                    else:
                        self.play_debuff_sound()

                    # Add pickup text
                    if hasattr(self, 'add_pickup_text'):
                        self.add_pickup_text(message, self.player.center_x, self.player.center_y)
                    elif hasattr(self, 'pickup_texts'):
                        self.pickup_texts.append([message, self.player.center_x, self.player.center_y, 1.0])
                except Exception as e:
                    print(f"Error applying orb effect: {e}")

        # Check bullet collisions
        for enemy in self.enemies:
            if hasattr(enemy, 'bullets'):
                # Enemy bullets hit player
                if self.player and not getattr(self.player, 'invincible', False):
                    bullet_hit_list = arcade.check_for_collision_with_list(self.player, enemy.bullets)
                    for bullet in bullet_hit_list:
                        # Remove the bullet
                        bullet.remove_from_sprite_lists()

                        # Damage player
                        damage = getattr(bullet, 'damage', 1)
                        self.player.take_damage(damage)
                        
                        # Play damage sound
                        self.play_damage_sound()
        
    def show_shop(self):
        """Show the shop view."""
        shop_view = ShopView(self.player, self)
        self.window.show_view(shop_view)
        
    def show_message(self, message, duration=2.0):
        """
        Show a message on screen.

        Args:
            message (str): The message to display
            duration (float): How long to display the message in seconds
        """
        self.message = message
        self.message_timer = duration
        print(f"📢 Showing message: {message}")
        
    def get_screen_dimensions(self):
        """Get the dimensions of the game screen."""
        # Use the window dimensions if width/height attributes don't exist
        window = arcade.get_window()
        return window.width, window.height

    def draw_hud(self):
        """Draw the heads-up display."""
        # Draw player health
        if hasattr(self.player, 'draw_hearts'):
            self.player.draw_hearts()

        # Draw score
        arcade.draw_text(f"Score: {int(self.score)}", 30, arcade.get_window().height - 60, 
                         arcade.color.WHITE, 16)

        # Draw coin count
        if hasattr(self.player, 'coins'):
            arcade.draw_text(f"Coins: {self.player.coins}", arcade.get_window().width - 100, 30, 
                             arcade.color.GOLD, 18)

        # Draw wave info
        if hasattr(self, 'wave_manager'):
            # Draw wave number
            wave_number = self.wave_manager.wave if hasattr(self.wave_manager, 'wave') else 1
            color = arcade.color.GOLD if wave_number % 5 == 0 else arcade.color.LIGHT_GREEN
            arcade.draw_text(
                f"Wave {wave_number}",
                arcade.get_window().width // 2,
                arcade.get_window().height - 35,
                color,
                font_size=18,
                anchor_x="center"
            )

            # Draw wave timer if in a wave
            if hasattr(self, 'in_wave') and self.in_wave and hasattr(self, 'level_timer') and hasattr(self, 'wave_duration'):
                time_left = max(0, int(self.wave_duration - self.level_timer))
                arcade.draw_text(f"⏱ {time_left}s left", arcade.get_window().width // 2, 
                                 arcade.get_window().height - 70, arcade.color.LIGHT_GRAY, 16, 
                                 anchor_x="center")

        # Draw wave message only if not already drawn by wave manager
        if hasattr(self, 'wave_message') and hasattr(self, 'wave_message_alpha') and self.wave_message_alpha > 0:
            # Check if wave manager has already drawn this message
            wave_manager_drew_message = False
            if hasattr(self, 'wave_manager') and hasattr(self.wave_manager, 'last_message_drawn'):
                wave_manager_drew_message = (self.wave_manager.last_message_drawn == self.wave_message)

            # Only draw if not already drawn
            if not wave_manager_drew_message:
                color = arcade.color.LIGHT_GREEN
                arcade.draw_text(
                    self.wave_message,
                    arcade.get_window().width / 2,
                    arcade.get_window().height / 2,
                    color,
                    font_size=24,
                    anchor_x="center"
                )
                
        # Draw buff display
        if hasattr(self, 'buff_display_text'):
            y_offset = arcade.get_window().height - 100
            for buff_text in self.buff_display_text:
                arcade.draw_text(
                    buff_text,
                    30,
                    y_offset,
                    arcade.color.LIGHT_BLUE,
                    font_size=14
                )
                y_offset -= 20

    def add_pickup_text(self, text, x, y):
        """Add a pickup text that floats upward and fades out."""
        if not hasattr(self, 'pickup_texts'):
            self.pickup_texts = []

        # Add the text with position and lifetime
        self.pickup_texts.append(PickupText(text, x, y))  # 1.0 second lifetime

    def apply_skin_toggle(self):
        """Toggle between available skins"""
        # Get available skins
        available_skins = list(skin_manager.skin_data.keys())
        current_skin = skin_manager.current_skin

        # Find next skin
        if current_skin in available_skins:
            current_index = available_skins.index(current_skin)
            next_index = (current_index + 1) % len(available_skins)
            next_skin = available_skins[next_index]

            # Apply new skin
            if skin_manager.set_skin(next_skin):
                print(f"🎨 Skin set to: {next_skin}")
                print(f"Skin changed to: {next_skin}")

                # Update player texture
                if self.player:
                    self.player.texture = skin_manager.get_texture("player", None)

                    # Update heart textures
                    self.player.heart_textures = {
                        "red": skin_manager.get_texture("ui", "heart_red"),
                        "gray": skin_manager.get_texture("ui", "heart_gray"),
                        "gold": skin_manager.get_texture("ui", "heart_gold")
                    }
            else:
                print(f"⚠️ Failed to switch skin")
        else:
            print(f"⚠️ Current skin '{current_skin}' not found in available skins")

    def on_key_press(self, key, modifiers):
        """Handle key press events"""
        if key == arcade.key.ESCAPE:
            # Pause the game or return to menu
            pass
        elif key == arcade.key.SPACE:
            # Player dash
            if self.player:
                self.player.try_dash()
        elif key == arcade.key.T:
            # Toggle skin
            self.apply_skin_toggle()

    def on_mouse_press(self, x, y, button, modifiers):
        """Handle mouse press events."""
        # Store mouse position
        self.mouse_x = x
        self.mouse_y = y

        if button == arcade.MOUSE_BUTTON_RIGHT:
            # Convert screen coordinates to world coordinates if using camera
            if hasattr(self, 'camera'):
                # Different versions of Arcade have different methods for coordinate conversion
                # Try the appropriate method based on your Arcade version
                try:
                    # For newer Arcade versions
                    world_pos = self.camera.mouse_coordinates_to_world(x, y)
                    x, y = world_pos
                except AttributeError:
                    # For older Arcade versions or custom Camera implementations
                    # Calculate the conversion manually
                    x = x / self.camera.scale + self.camera.position[0]
                    y = y / self.camera.scale + self.camera.position[1]
                    print(f"Converted mouse position to world coordinates: ({x}, {y})")

            # Set player target
            if self.player:
                self.player.set_target(x, y)
            self.right_mouse_down = True
            print(f"🖱️ Right mouse button pressed")
        elif button == arcade.MOUSE_BUTTON_LEFT:
            self.left_mouse_down = True
            
            # Set target position for player
            if self.player:
                self.player.set_target(x, y)
            
            print("🖱️ Left mouse button pressed")

    def on_mouse_release(self, x, y, button, modifiers):
        """Handle mouse release events."""
        # Update mouse position
        self.mouse_x = x
        self.mouse_y = y

        # Update mouse button state
        if button == arcade.MOUSE_BUTTON_LEFT:
            self.left_mouse_down = False
            print("🖱️ Left mouse button released")
        elif button == arcade.MOUSE_BUTTON_RIGHT:
            self.right_mouse_down = False
            print("🖱️ Right mouse button released")

    def on_mouse_release(self, x, y, button, modifiers):
        """Handle mouse release events"""
        if button == arcade.MOUSE_BUTTON_RIGHT:
            self.right_mouse_down = False

    def on_mouse_motion(self, x, y, dx, dy):
        """Handle mouse motion events."""
        # Update mouse position
        self.mouse_x = x
        self.mouse_y = y

        # If either mouse button is held down, update player target
        if (self.left_mouse_down or self.right_mouse_down) and self.player:
            self.player.set_target(x, y)

    def show_wave_message(self, text):
        self.wave_message = text
        self.wave_message_alpha = 255
        self.message_timer = 0  # reset
        
    def show_pickup_text(self, text, color=arcade.color.WHITE, x=None, y=None):
        if x is None or y is None:
            x, y = self.player.center_x, self.player.center_y + 30
        text_obj = arcade.Text(text, x, y, color, font_size=12, anchor_x="center")
        self.pickup_texts.append(text_obj)