class DifficultyAdjuster:
    def __init__(self):
        self.base_difficulty = 0.5  # 0.0 to 1.0
        self.challenge_preference = 0.5  # How much challenge the player seems to enjoy
        self.learning_rate = 0.1  # How quickly we adjust to player performance

    def calculate_parameters(self, wave_number, player_profile, engagement_score):
        """Calculate difficulty parameters for the next wave"""
        # Base difficulty increases with wave number
        wave_difficulty = min(0.9, 0.3 + (wave_number * 0.03))

        # Adjust based on player skill
        skill_adjustment = (player_profile["skill_level"] - 0.5) * 0.5

        # Adjust based on engagement (if player is bored, increase challenge)
        engagement_adjustment = (0.7 - engagement_score) * 0.3

        # Calculate final difficulty
        difficulty = wave_difficulty + skill_adjustment + engagement_adjustment
        difficulty = max(0.1, min(1.0, difficulty))

        # Generate specific parameters based on difficulty
        return {
            "difficulty": difficulty,
            "enemy_count": self._calculate_enemy_count(difficulty, wave_number),
            "enemy_speed": self._calculate_enemy_speed(difficulty),
            "enemy_health": self._calculate_enemy_health(difficulty),
            "enemy_types": self._determine_enemy_types(difficulty, player_profile),
            "orb_count": self._calculate_orb_count(difficulty, wave_number),
            "orb_types": self._determine_orb_types(player_profile),
            "spawn_artifact": self._should_spawn_artifact(wave_number, player_profile)
        }
    def _calculate_enemy_count(self, difficulty, wave_number):
        """Calculate number of enemies based on difficulty"""
        base_count = 3 + wave_number + wave_number // 3
        difficulty_modifier = difficulty * 0.5
        return min(25, int(base_count * (1 + difficulty_modifier)))

    def _calculate_enemy_speed(self, difficulty):
        """Calculate enemy speed multiplier"""
        return 0.8 + (difficulty * 0.4)

    def _calculate_enemy_health(self, difficulty):
        """Calculate enemy health multiplier"""
        return 0.8 + (difficulty * 0.4)

    def _determine_enemy_types(self, difficulty, player_profile):
        """Determine enemy type distribution based on difficulty and player profile"""
        types = ["chaser", "wander"]

        if difficulty > 0.4:
            types.append("shooter")

        if difficulty > 0.6:
            types.append("flight")
            
        if difficulty > 0.75:
            types.append("bomber")

        # Adjust based on player's playstyle
        if player_profile["playstyle"]["aggression"] > 0.7:
            # Aggressive players get more defensive enemies
            return {"chaser": 0.2, "wander": 0.2, "shooter": 0.4, "bomber": 0.2}
        elif player_profile["playstyle"].get("caution", 0) > 0.7:
            # Cautious players get more aggressive enemies
            return {"chaser": 0.4, "wander": 0.2, "shooter": 0.2, "bomber": 0.2}
        else:
            # Balanced distribution
            return {t: 1.0/len(types) for t in types}

    def _calculate_orb_count(self, difficulty, wave_number):
        """Calculate number of orbs to spawn"""
        if wave_number < 5:
            return 0
        elif wave_number < 10:
            return 1
        elif wave_number < 15:
            return 2
        else:
            return 3

    def _determine_orb_types(self, player_profile):
        """Determine orb type distribution based on player preferences"""
        # Default distribution
        distribution = {"buff": 0.8, "debuff": 0.2}

        # If player has preferences, slightly adjust toward less-used types
        preferences = player_profile.get("preferences", {})
        orb_pref = preferences.get("orb_preference", None)
        if orb_pref:
            # Implementation would adjust based on usage patterns
            pass

        return distribution

    def _should_spawn_artifact(self, wave_number, player_profile):
        """Determine if an artifact should spawn"""
        return wave_number % 5 == 0

    def adjust_based_on_performance(self, wave_stats: dict):
        """
        Adjust base difficulty based on player performance from the last wave.
        This method allows adaptive scaling as the player progresses.

        Args:
            wave_stats (dict): Dictionary with keys like 'damage_taken', 
                               'time_survived', 'buffs_collected', 'debuffs_collected',
                               'coins_collected', 'heatmap_entropy'.
        """
        # Default to zero if key is missing
        damage_taken = wave_stats.get("damage_taken", 0)
        time_survived = wave_stats.get("time_survived", 0)
        buffs = wave_stats.get("buffs_collected", 0)
        debuffs = wave_stats.get("debuffs_collected", 0)
        entropy = wave_stats.get("heatmap_entropy", 0.5)

        # Normalize and weight
        damage_factor = max(0.0, 1.0 - (damage_taken / 100))  # Less damage = better
        survival_factor = min(1.0, time_survived / 60.0)  # Cap at 60 seconds
        buff_efficiency = buffs - debuffs  # More buffs than debuffs = good
        movement_score = entropy  # Higher entropy = more dynamic play

        # Simple weighted average for performance score
        performance_score = (
            (damage_factor * 0.4)
            + (survival_factor * 0.3)
            + (max(0.0, min(buff_efficiency / 5.0, 1.0)) * 0.2)
            + (movement_score * 0.1)
        )

        # Smooth update of base difficulty
        old_difficulty = self.base_difficulty
        self.base_difficulty = (
            (1.0 - self.learning_rate) * self.base_difficulty
            + self.learning_rate * performance_score
        )

        print(f"[AI Tuning] 📊 PerfScore: {performance_score:.2f} | "
              f"Old Diff: {old_difficulty:.2f} → New Diff: {self.base_difficulty:.2f}")
              
    def update_player_profile(self, player_profile: dict, wave_stats: dict):
        """
        Adjusts the player profile based on recent dodging performance (non-combat).
        """
        def smooth(old, new, rate=0.1):
            return (1 - rate) * old + rate * new

        # Bravery: Do they cut it close?
        dodge_bravery = wave_stats.get("close_calls", 5) / (wave_stats.get("total_dodges", 10) + 1)

        # Risk: How chaotic is their movement?
        chaos_tolerance = wave_stats.get("heatmap_entropy", 0.5)

        # Skill: How well do they survive?
        survival = wave_stats.get("time_survived", 30)
        hearts_lost = wave_stats.get("hearts_lost", 1)
        skill_score = min(1.0, (survival / 60) * (1.0 - hearts_lost / 3))

        # Orb preference
        buffs = wave_stats.get("buffs_collected", 0)
        debuffs = wave_stats.get("debuffs_collected", 0)
        orb_pref = buffs / (buffs + debuffs + 1)

        # Update
        player_profile["playstyle"]["bravery"] = smooth(player_profile["playstyle"].get("bravery", 0.5), dodge_bravery)
        player_profile["playstyle"]["chaos"] = smooth(player_profile["playstyle"].get("chaos", 0.5), chaos_tolerance)
        player_profile["skill_level"] = smooth(player_profile.get("skill_level", 0.5), skill_score)

        if "preferences" not in player_profile:
            player_profile["preferences"] = {}
        player_profile["preferences"]["orb_preference"] = smooth(
            player_profile["preferences"].get("orb_preference", 0.5), orb_pref
        )

        print(f"[🧠 PROFILE] Bravery: {player_profile['playstyle']['bravery']:.2f} | "
              f"Chaos: {player_profile['playstyle']['chaos']:.2f} | "
              f"Skill: {player_profile['skill_level']:.2f} | "
              f"Orbs: {player_profile['preferences']['orb_preference']:.2f}")
