easy_workouts = {
    "30_min_easy": [
        (1.2, 600),  # 10 min slow walk  
        (1.5, 600),  # 10 min comfortable pace  
        (1.8, 600),  # 10 min slightly brisk walk  
    ],
    "60_min_easy": [
        (1.2, 900),  # 15 min slow walk  
        (1.5, 900),  # 15 min comfortable pace  
        (1.8, 900),  # 15 min slightly brisk walk  
        (1.2, 900),  # 15 min cooldown walk  
    ],
}

import json

with open("easy_workouts.json", "w") as f:
    json.dump(easy_workouts, f, indent=4)

print("Easy workouts saved to easy_workouts.json")
