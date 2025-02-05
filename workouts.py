# 20-Minute HIIT Sprint Workout
workout_20min = [
    (3, 120),  # Warm-up
    (10, 30),
    (4, 60),  # Sprint & Recovery
    (11, 30),
    (4, 60),
    (12, 30),
    (5, 60),
    (10, 30),
    (5, 60),
    (11, 30),
    (5, 60),
    (12, 30),
    (6, 60),
    (10, 30),
    (6, 60),
    (12, 30),
    (6, 60),
    (3, 120),  # Cool-down
]

# 30-Minute Endurance Run
workout_30min = [
    (3, 180),  # Warm-up
    (6, 300),
    (7, 300),
    (8, 300),
    (9, 300),
    (10, 300),
    (8, 300),
    (6, 300),
    (3, 180),  # Cool-down
]

# 40-Minute Interval Challenge
workout_40min = [
    (3, 240),  # Warm-up
    (7, 600),
    (10, 45),
    (5, 60),
    (11, 45),
    (5, 60),
    (12, 30),
    (6, 90),
    (10, 45),
    (5, 90),
    (11, 45),
    (5, 90),
    (12, 30),
    (6, 120),
    (8, 300),
    (3, 240),  # Cool-down
]

# 50-Minute Progression Run
workout_50min = [
    (3, 300),  # Warm-up
    (5, 300),
    (6, 300),
    (7, 300),
    (8, 300),
    (9, 300),
    (10, 300),
    (11, 300),
    (12, 300),
    (10, 300),
    (8, 300),
    (6, 300),
    (3, 300),  # Cool-down
]

# 60-Minute Mixed Terrain Simulation
workout_60min = [
    (3, 300),  # Warm-up
    (6, 600),
    (8, 600),
    (10, 300),
    (6, 300),
    (12, 45),
    (6, 90),
    (11, 60),
    (6, 120),
    (9, 600),
    (7, 600),
    (10, 300),
    (6, 300),
    (11, 60),
    (6, 120),
    (12, 30),
    (6, 90),
    (7, 600),
    (3, 300),  # Cool-down
]

min_30_easy = [
    (1.2, 600),  # 10 min slow walk
    (1.5, 600),  # 10 min comfortable pace
    (1.8, 600),  # 10 min slightly brisk walk
]

min_60_easy = [
    (1.2, 900),  # 15 min slow walk
    (1.5, 900),  # 15 min comfortable pace
    (1.8, 900),  # 15 min slightly brisk walk
    (1.2, 900),  # 15 min cooldown walk
]


workouts = {
    "20_min_HIIT": workout_20min,
    "30_min_endurance": workout_30min,
    "40_min_intervals": workout_40min,
    "50_min_progression": workout_50min,
    "60_min_mixed": workout_60min,
    "30_min_easy": min_30_easy,
    "60_min_easy": min_60_easy,
}
