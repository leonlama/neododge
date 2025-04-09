from src.mechanics.wave_management.difficulty_adjuster import DifficultyAdjuster

def test_adjust_based_on_performance_updates_difficulty():
    adjuster = DifficultyAdjuster()
    old_difficulty = adjuster.base_difficulty

    wave_stats = {
        "damage_taken": 10,
        "time_survived": 55,
        "buffs_collected": 3,
        "debuffs_collected": 1,
        "coins_collected": 10,
        "heatmap_entropy": 0.7,
    }

    adjuster.adjust_based_on_performance(wave_stats)

    assert adjuster.base_difficulty != old_difficulty, "Difficulty should update based on performance."
    assert 0 <= adjuster.base_difficulty <= 1, "Difficulty must stay between 0 and 1."

def test_update_profile_for_dodging_game():
    adjuster = DifficultyAdjuster()
    profile = {
        "playstyle": {"bravery": 0.5, "chaos": 0.5},
        "skill_level": 0.5,
        "preferences": {"orb_preference": 0.5}
    }

    wave_stats = {
        "close_calls": 12,
        "total_dodges": 20,
        "time_survived": 50,
        "hearts_lost": 0,
        "buffs_collected": 3,
        "debuffs_collected": 0,
        "heatmap_entropy": 0.8
    }

    adjuster.update_player_profile(profile, wave_stats)

    assert 0 <= profile["playstyle"]["bravery"] <= 1
    assert 0 <= profile["playstyle"]["chaos"] <= 1
    assert 0 <= profile["skill_level"] <= 1
    assert 0 <= profile["preferences"]["orb_preference"] <= 1
