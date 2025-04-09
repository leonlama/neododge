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
