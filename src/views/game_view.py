import arcade
import random
from src.controllers.game_controller import GameController
from src.entities.player.player import Player
from src.core.constants import SCREEN_WIDTH, SCREEN_HEIGHT
from src.skins.skin_manager import skin_manager
from src.audio.sound_manager import sound_manager

from src.mechanics.artifacts.dash_artifact import DashArtifact
from src.mechanics.coins.coin import Coin
from src.mechanics.orbs.orb_pool import get_random_orb
from src.views.shop_view import ShopView

from src.mechanics.wave_management.wave_manager import WaveManager
from src.controllers.game_controller import GameController
from src.ui.improved_hud import draw_hud, draw_wave_message, draw_pickup_texts

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

    def setup(self):
        """Set up the game."""
        # Create player
        self.player = Player(self.window.width // 2, self.window.height // 2)
        self.player.window = self.window
        self.player.parent_view = self
        
        # Load heart textures from skin manager
        self.heart_textures = {
            "red": skin_manager.get_texture("ui", "heart_red"),
            "gray": skin_manager.get_texture("ui", "heart_gray"),
            "gold": skin_manager.get_texture("ui", "heart_gold")
        }
        # Already loaded, or will fallback in player.draw_hearts()
        
        # Pass heart textures to player
        self.player.heart_textures = self.heart_textures

        # Initialize sprite lists
        self.enemies = arcade.SpriteList()
        self.orbs = arcade.SpriteList()
        self.coins = arcade.SpriteList()
        self.artifacts = arcade.SpriteList()

        # Set up wave manager
        self.setup_wave_manager()

        # Create wave manager
        from src.mechanics.wave_management.wave_manager import WaveManager
        self.wave_manager = WaveManager(self)

        # Ensure wave manager has required attributes
        if not hasattr(self.wave_manager, 'current_wave'):
            self.wave_manager.current_wave = getattr(self.wave_manager, 'wave', 1)

        if not hasattr(self.wave_manager, 'wave_timer'):
            self.wave_manager.wave_timer = 0

        # Initialize dash artifact (but don't spawn it yet)
        self.dash_artifact = None

        # Set up coin spawning (start with a delay)
        self.coins_to_spawn = 5
        self.coin_spawn_timer = 3.0  # First coin spawns after 3 seconds

        # Set up orb spawning
        self.orb_spawn_timer = random.uniform(4, 8)

        # Set up artifact spawning
        self.artifact_spawn_timer = random.uniform(20, 30)

        # Initialize other game state variables
        self.score = 0
        self.level_timer = 0.0
        self.wave_duration = 20.0
        self.in_wave = True
        self.wave_pause = False
        self.wave_message = ""
        self.wave_message_alpha = 0

        # Initialize pickup texts
        self.pickup_texts = []

        # Initialize game controller
        self.game_controller = GameController(self, self.window.width, self.window.height)

        # Load sounds using sound manager
        self.setup_sounds()

    def setup_wave_manager(self):
        """Set up the wave manager."""
        from src.mechanics.wave_management.wave_manager import WaveManager

        # Create wave manager
        self.wave_manager = WaveManager()

        # Set game view reference
        self.wave_manager.game_view = self

        # Set callbacks
        self.wave_manager.on_spawn_enemy = self.spawn_enemy
        self.wave_manager.on_clear_enemies = self.clear_enemies

        print("Wave manager set up with callbacks")

        # Start first wave
        self.wave_manager.start_wave()

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

    def spawn_artifact(self):
        """Spawn a random artifact."""
        # Random position
        x = random.randint(50, self.window.width - 50)
        y = random.randint(50, self.window.height - 50)

        # Random artifact type
        artifact_type = random.choice(["damage", "speed", "health", "shield"])

        # Create artifact
        artifact = Artifact(x, y, artifact_type)

        # Add to sprite lists
        self.artifacts.append(artifact)
        self.all_sprites.append(artifact)

    def clear_enemies(self):
        """Clear all enemies from the screen."""
        self.enemies = arcade.SpriteList()

    def on_wave_start(self, wave_number):
        """Called when a wave starts."""
        print(f"Wave {wave_number} started!")

        # Show wave message
        self.wave_message = f"Wave {wave_number}"
        self.wave_message_alpha = 1.0

        # Spawn some coins and orbs
        self.spawn_coins(5)
        self.spawn_orbs(2)

    def on_wave_end(self, wave_number):
        """Called when a wave ends."""
        print(f"Wave {wave_number} completed!")

        # Show wave complete message
        self.wave_message = f"Wave {wave_number} Complete!"
        self.wave_message_alpha = 1.0
        
        # Increment score
        self.score += wave_number * 100

        # Spawn coins as a reward
        self.spawn_coins(wave_number * 2)

        # Start the next wave after a delay
        arcade.schedule(self.start_next_wave, 2.0)
        
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
            self.clear()
            
            # Draw background
            if hasattr(self, 'background') and self.background:
                self.background.draw()
    
            # Use game camera for game elements
            self.camera.use()
    
            # Draw player
            if hasattr(self, 'player') and self.player:
                self.player.draw()
    
            # Draw enemies with debug info
            if hasattr(self, 'enemies'):
                self.enemies.draw()
                
                # Debug: Draw enemy count and positions
                for i, enemy in enumerate(self.enemies):
                    # Draw a bright outline around each enemy to make them more visible
                    arcade.draw_circle_outline(
                        enemy.center_x, enemy.center_y, 
                        enemy.width / 2 + 5, 
                        arcade.color.YELLOW, 2
                    )
    
            # Draw orbs
            if hasattr(self, 'orbs'):
                self.orbs.draw()
    
            # Draw coins
            if hasattr(self, 'coins'):
                self.coins.draw()
    
            # Draw artifacts
            if hasattr(self, 'artifacts'):
                self.artifacts.draw()
    
            # Draw enemy bullets
            for enemy in self.enemies:
                if hasattr(enemy, 'bullets'):
                    enemy.bullets.draw()
    
            # Use GUI camera for UI elements
            self.gui_camera.use()
    
            # Draw HUD
            if hasattr(self, 'draw_hud'):
                self.draw_hud()
            else:
                try:
                    self.draw_improved_hud()
                except Exception as e:
                    print(f"Error drawing HUD: {e}")
                    # Fallback to simple HUD
                    self.draw_simple_hud()
            
            # Debug: Draw enemy count
            arcade.draw_text(f"Enemies: {len(self.enemies)}", 10, 40, arcade.color.WHITE, 14)
            
            # Draw player status effects
            if hasattr(self, 'player') and self.player:
                self.player.draw_effects(self.window.width, self.window.height)
            
            # Draw active buffs
            self.draw_buffs()
    
            # Draw any pickup texts
            if hasattr(self, 'pickup_texts'):
                draw_pickup_texts(self.pickup_texts)
    
            # Draw wave message if active
            if hasattr(self, 'wave_message') and hasattr(self, 'wave_message_alpha') and self.wave_message_alpha > 0:
                draw_wave_message(self.wave_message, int(255 * self.wave_message_alpha))
    
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
        self.pickup_texts.append([text, x, y, 1.0])  # 1.0 second lifetime

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

    def on_update(self, delta_time):
        """Update game state."""
        # Update player
        if self.player:
            self.player.update(delta_time)

        # Update wave manager
        if hasattr(self, 'wave_manager'):
            self.wave_manager.update(delta_time)

        # If right mouse is held down, continuously update target
        if self.right_mouse_down and self.player:
            self.player.set_target(self.mouse_x, self.mouse_y)

        # Update game controller
        if hasattr(self, 'game_controller'):
            self.game_controller.update(delta_time)

        # Check if we should show the shop
        if self.game_controller.should_show_shop():
            # Show shop view
            from src.views.shop_view import ShopView
            shop_view = ShopView()
            shop_view.player = self.player
            shop_view.previous_view = self
            self.window.show_view(shop_view)

            # Reset shop flag to prevent showing it again immediately
            self.game_controller.reset_shop_flag()
            return

        # Update enemies
        for enemy in self.enemies:
            # Set target if needed
            if hasattr(enemy, 'set_target') and hasattr(enemy, 'target') and enemy.target is None:
                enemy.set_target(self.player)

            # Update enemy
            if hasattr(enemy, 'update'):
                enemy.update(delta_time)
            else:
                # Basic update for fallback enemies
                enemy.center_x += getattr(enemy, 'change_x', 0)
                enemy.center_y += getattr(enemy, 'change_y', 0)

        # Update enemy bullets
        self.update_enemies(delta_time)

        # Update orbs
        for orb in self.orbs:
            orb.update()

        # Update coins
        for coin in self.coins:
            coin.update()
            # Update coin animations
            if hasattr(coin, 'update_animation'):
                coin.update_animation(delta_time)

        # Update artifacts
        for artifact in self.artifacts:
            artifact.update()

        # Update message timer
        if hasattr(self, 'message') and self.message:
            self.message_timer += delta_time
            if self.message_timer >= self.message_duration:
                self.message = None

        # Handle coin spawning
        if hasattr(self, 'coins_to_spawn') and self.coins_to_spawn > 0:
            if hasattr(self, 'coin_spawn_timer'):
                self.coin_spawn_timer -= delta_time
                if self.coin_spawn_timer <= 0:
                    # Spawn a coin at a random position
                    x = random.randint(50, arcade.get_window().width - 50)
                    y = random.randint(50, arcade.get_window().height - 50)

                    # Create the coin
                    coin = Coin(x, y)
                    self.coins.append(coin)

                    # Update spawn counter and timer
                    self.coins_to_spawn -= 1
                    self.coin_spawn_timer = random.uniform(3, 7)  # Random time until next coin
                    print(f"🪙 Spawned a coin! Remaining: {self.coins_to_spawn}")

        # Handle orb spawning
        if hasattr(self, 'orb_spawn_timer'):
            self.orb_spawn_timer -= delta_time
            if self.orb_spawn_timer <= 0:
                # Spawn an orb at a random position
                x = random.randint(50, arcade.get_window().width - 50)
                y = random.randint(50, arcade.get_window().height - 50)

                # Create a random orb using the orb pool with context
                orb = get_random_orb(x, y, context={
                    "wave": self.wave_manager.current_wave,
                    "hp": self.player.current_hearts,
                    "mult": self.player.score_multiplier
                })
                self.orbs.append(orb)

                # Reset timer
                self.orb_spawn_timer = random.uniform(4, 8)
                print(f"🔮 Spawned an orb!")

        # Handle artifact spawning
        if hasattr(self, 'artifact_spawn_timer'):
            self.artifact_spawn_timer -= delta_time
            if self.artifact_spawn_timer <= 0 and not hasattr(self, 'dash_artifact'):
                # Spawn an artifact at a random position
                x = random.randint(50, arcade.get_window().width - 50)
                y = random.randint(50, arcade.get_window().height - 50)

                # Create the artifact
                self.dash_artifact = DashArtifact(x, y)
                self.artifacts.append(self.dash_artifact)

                # Reset timer
                self.artifact_spawn_timer = random.uniform(20, 30)
                print("✨ Spawned a dash artifact!")

        # Update pickup texts
        if hasattr(self, 'pickup_texts'):
            for i in range(len(self.pickup_texts) - 1, -1, -1):
                text, x, y, lifetime = self.pickup_texts[i]
                lifetime -= delta_time
                if lifetime <= 0:
                    self.pickup_texts.pop(i)
                else:
                    # Move text upward
                    self.pickup_texts[i] = [text, x, y + 1, lifetime]

        # Update wave message alpha
        if hasattr(self, 'wave_message_alpha') and self.wave_message_alpha > 0:
            self.wave_message_alpha -= delta_time * 0.5  # Fade out over 2 seconds

        # Check for collisions
        self.check_collisions()
        
        # Check for orb collisions
        self.check_orb_collisions()

        # Update score
        self.score += delta_time * 10

    def spawn_coins(self, count):
        """Spawn a number of coins."""
        self.coins_to_spawn = count
        self.coin_spawn_timer = 0.5  # Start spawning soon

    def spawn_orbs(self, orb_count, orb_types=None):
        """Spawn orbs with the given distribution.

        Args:
            orb_count: Number of orbs to spawn
            orb_types: Dictionary of orb types and their weights (optional)
        """
        if orb_types is None:
            # Default distribution if none provided
            orb_types = {"buff": 0.7, "debuff": 0.3}

        for _ in range(orb_count):
            # Determine orb type based on distribution
            orb_type = random.choices(
                list(orb_types.keys()),
                weights=list(orb_types.values())
            )[0]

            # Random position
            x = random.randint(50, self.window.width - 50)
            y = random.randint(50, self.window.height - 50)

            # Create orb with type information
            self.spawn_orb(x, y, orb_type=orb_type)
            
    def spawn_orb(self, x=None, y=None):
        """Spawn an orb at the specified position or a random position."""
        if x is None or y is None:
            # Random position within the screen
            x = random.randint(50, self.window.width - 50)
            y = random.randint(50, self.window.height - 50)

        # Create context with current wave number
        context = {
            'wave': self.wave_manager.current_wave if hasattr(self, 'wave_manager') else 1,
            'player_health': self.player.current_hearts,
            'player_speed': self.player.speed
        }

        # Get a random orb
        orb = get_random_orb(x, y, context=context)

        # Add to orbs list
        self.orbs.append(orb)
        #print(f"Spawned orb at ({x}, {y})")
            
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

            # Remove the orb
            orb.remove_from_sprite_lists()

            # Update analytics
            if hasattr(self, 'wave_manager') and hasattr(self.wave_manager, 'wave_analytics'):
                self.wave_manager.wave_analytics.update_wave_stat(self.wave_manager.wave, "orbs_collected", 1)
                
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
        enemy_hit_list = arcade.check_for_collision_with_list(self.player, self.enemies)
        for enemy in enemy_hit_list:
            # Handle player taking damage
            if hasattr(self.player, 'take_damage'):
                self.player.take_damage()
                
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
        #print(f"Checking orb collisions. Player at ({self.player.center_x}, {self.player.center_y})")
        #print(f"Number of orbs: {len(self.orbs)}")

        # Use a more reliable collision detection method
        for orb in list(self.orbs):  # Use a copy of the list to safely modify during iteration
            distance = ((self.player.center_x - orb.center_x) ** 2 + 
                        (self.player.center_y - orb.center_y) ** 2) ** 0.5
            #print(f"Orb at ({orb.center_x}, {orb.center_y}), Distance: {distance}")

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

        # The original arcade.check_for_collision_with_list as a backup
        orb_hit_list = arcade.check_for_collision_with_list(self.player, self.orbs)
        #print(f"Orb hit list length: {len(orb_hit_list)}")

        # Process any hits found by arcade's collision detection (unlikely if our custom detection worked)
        for orb in orb_hit_list:
            if orb in self.orbs:  # Make sure it wasn't already removed
                print(f"Arcade collision detected with {orb.orb_type} orb!")
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

        # Enemy bullet collisions with player
        for enemy in self.enemies:
            if hasattr(enemy, 'bullets'):
                bullet_hit_list = arcade.check_for_collision_with_list(self.player, enemy.bullets)
                for bullet in bullet_hit_list:
                    # Remove the bullet
                    bullet.remove_from_sprite_lists()

                    # Handle player taking damage
                    if hasattr(self.player, 'take_damage'):
                        self.player.take_damage(1)
                        
                        # Play damage sound
                        self.play_damage_sound()

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
            self.player.speed_multiplier = 0.5
            self.player.slow_timer = 4.0  # 4 seconds
            print(f"Applied slow debuff: {self.player.speed_multiplier}x for {self.player.slow_timer}s")

        elif orb_type == "hitbox":
            # Hitbox debuff (similar to damage)
            if hasattr(self.player, 'take_damage'):
                self.player.take_damage()
            print(f"Applied hitbox debuff: -1 health")

        # Update buff display
        self.update_buff_display()
        
    def show_shop(self):
        """Show the shop view."""
        shop_view = ShopView(self.player, self)
        self.window.show_view(shop_view)
        
    def show_message(self, message, duration=2.0):
        """Show a message on the screen."""
        self.message = message
        self.message_timer = 0
        self.message_duration = duration
        
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
        self.pickup_texts.append([text, x, y, 1.0])  # 1.0 second lifetime

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
        """Handle mouse press events"""
        if button == arcade.MOUSE_BUTTON_RIGHT:
            # Set player target with right click
            if self.player:
                self.player.set_target(x, y)
                self.right_mouse_down = True
                self.mouse_x = x
                self.mouse_y = y

    def on_mouse_release(self, x, y, button, modifiers):
        """Handle mouse release events"""
        if button == arcade.MOUSE_BUTTON_RIGHT:
            self.right_mouse_down = False

    def on_mouse_motion(self, x, y, dx, dy):
        """Handle mouse motion events"""
        self.mouse_x = x
        self.mouse_y = y