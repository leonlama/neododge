import arcade
import random
from src.entities.player.player import Player
from src.skins.skin_manager import skin_manager
from src.controllers.game_controller import GameController
from src.core.constants import WAVE_DURATION
from src.mechanics.wave_management.wave_analytics import WaveAnalytics
from src.mechanics.wave_management.wave_generator import WaveGenerator
from src.mechanics.wave_management.wave_manager import WaveManager


def setup_game(game_view):
        """Set up the game."""
        # Import spawn methods
        from src.views.game.spawn_logic import (
            spawn_enemy,
            clear_enemies,
            spawn_artifact,
            spawn_orbs,
            spawn_coin,
        )
        
        # Bind spawn methods to game_view
        game_view.spawn_enemy = lambda *args, **kwargs: spawn_enemy(game_view, *args, **kwargs)
        game_view.clear_enemies = lambda *args, **kwargs: clear_enemies(game_view, *args, **kwargs)
        game_view.spawn_artifact = lambda *args, **kwargs: spawn_artifact(game_view, *args, **kwargs)
        game_view.spawn_orbs = lambda *args, **kwargs: spawn_orbs(game_view, *args, **kwargs)
        game_view.spawn_coin = lambda *args, **kwargs: spawn_coin(game_view, *args, **kwargs)
        
        # Create sprite lists
        game_view.enemies = arcade.SpriteList()
        game_view.orbs = arcade.SpriteList()
        game_view.coins = arcade.SpriteList()
        game_view.artifacts = arcade.SpriteList()
        game_view.bullets = arcade.SpriteList()

        # Initialize mouse state
        game_view.left_mouse_down = False
        game_view.right_mouse_down = False
        game_view.mouse_x = 0
        game_view.mouse_y = 0
        
        # Create player
        game_view.player = Player(game_view.window.width // 2, game_view.window.height // 2)
        game_view.player.window = game_view.window
        game_view.player.parent_view = game_view
        
        # Load heart textures from skin manager
        game_view.heart_textures = {
            "red": skin_manager.get_texture("ui", "heart_red"),
            "gray": skin_manager.get_texture("ui", "heart_gray"),
            "gold": skin_manager.get_texture("ui", "heart_gold")
        }
        # Already loaded, or will fallback in player.draw_hearts()
        
        # Pass heart textures to player
        game_view.player.heart_textures = game_view.heart_textures

        # Set up wave manager
        setup_wave_manager(game_view)

        # Ensure wave manager has required attributes
        if not hasattr(game_view.wave_manager, 'current_wave'):
            game_view.wave_manager.current_wave = getattr(game_view.wave_manager, 'wave', 1)

        if not hasattr(game_view.wave_manager, 'wave_timer'):
            game_view.wave_manager.wave_timer = 0

        # Initialize dash artifact (but don't spawn it yet)
        game_view.dash_artifact = None

        # Set up coin spawning (start with a delay)
        game_view.coins_to_spawn = 5
        game_view.coin_spawn_timer = 3.0  # First coin spawns after 3 seconds

        # Set up orb spawning
        game_view.orb_spawn_timer = random.uniform(4, 8)

        # Set up artifact spawning
        game_view.artifact_spawn_timer = random.uniform(20, 30)

        # Initialize other game state variables
        game_view.score = 0
        game_view.level_timer = 0.0
        game_view.wave_duration = WAVE_DURATION
        game_view.in_wave = True
        game_view.wave_pause = False
        game_view.wave_message = ""
        game_view.wave_message_alpha = 255
        game_view.message_timer = 0
        game_view.message_duration = 2.0  # duration (in seconds) the message is shown

        # Initialize pickup texts
        game_view.pickup_texts = []

        # Initialize game controller
        game_view.game_controller = GameController(game_view, game_view.window.width, game_view.window.height)

        # Import audio functions
        from src.views.game.audio_logic import (
            play_coin_sound,
            play_buff_sound,
            play_debuff_sound,
            play_damage_sound,
            setup_sounds,
        )

        # Bind audio logic
        game_view.play_coin_sound = lambda: play_coin_sound(game_view)
        game_view.play_buff_sound = lambda: play_buff_sound(game_view)
        game_view.play_debuff_sound = lambda: play_debuff_sound(game_view)
        game_view.play_damage_sound = lambda: play_damage_sound(game_view)
        game_view.setup_sounds = lambda: setup_sounds(game_view)

        # Load sounds using sound manager
        game_view.setup_sounds()


def setup_wave_manager(game_view):
    """Set up the wave manager."""
    # Create analytics and wave generator
    wave_analytics = WaveAnalytics()
    wave_generator = WaveGenerator(wave_analytics)
    
    # Create wave manager with generator and spawn callback
    wave_manager = WaveManager(wave_generator, game_view.spawn_enemy)
    
    # Attach to the game_view
    game_view.wave_manager = wave_manager
    
    # Make analytics explicitly available on the wave manager
    game_view.wave_manager.wave_analytics = wave_analytics
    
    # Set game view reference
    game_view.wave_manager.game_view = game_view
    
    # Set callbacks directly using bound methods
    game_view.wave_manager.on_spawn_enemy = game_view.spawn_enemy
    game_view.wave_manager.on_clear_enemies = game_view.clear_enemies

    # Set up callbacks dictionary
    game_view.wave_manager.callbacks = {
        "on_wave_start": game_view.on_wave_start,
        "on_wave_end": game_view.on_wave_end
    }

    print("Wave manager set up with callbacks and analytics")

    # Start first wave
    game_view.wave_manager.start_wave()