player = dict(
    base_radius=5,
    food_detection = 3,
    player_detection = 3,
    min_speed = 0.2,
    max_speed = 1.75,
    speed_reduction_rate = 40,
    eat_player_threshold = 0.10, # Dictates how much bigger a player must be to eat another player
    score_reduction = 0.998, # Dictates how much of the player's score is reduced every frame
    score_consumption = 0.45, # Dictates what percentage of the other players score this player absorbs when eating them
)

food = dict(
    value=1
)

game = dict(
    padding = 50,
    fps = 60,
    num_food = 450,
    max_score = 1000,
    frame_limit = 2000
)

neat = dict(
    max_score = 1000,
    max_gen = 10000,
)