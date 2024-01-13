import pygame


def draw_stats(selected_player, WIN, SCREEN_WIDTH):
    font = pygame.font.SysFont(None, 30)  # Adjust the size as needed
    score_text = font.render(
        f"Score: {selected_player.score:.0f}", True, (255, 255, 255)
    )  # White text
    num_players_text = font.render(
        f"Players Eaten: {selected_player.players_eaten}", True, (255, 255, 255)
    )
    num_food_text = font.render(
        f"Food Consumed: {selected_player.food_eaten}", True, (255, 255, 255)
    )
    location_text = font.render(
        f"Location: ({selected_player.x:.0f}, {selected_player.y:.0f})",
        True,
        (255, 255, 255),
    )
    conflicting_moves_text = font.render(
        f"Conflicting Moves: {selected_player.conflicting_moves}",
        True,
        (255, 255, 255),
    )
    in_motion_text = font.render(
        f"In Motion: {selected_player.in_motion}", True, (255, 255, 255)
    )
    stats_x = SCREEN_WIDTH - 300
    WIN.blit(score_text, (stats_x, 10))  # Position as needed
    WIN.blit(num_players_text, (stats_x, 40))  # Position as needed
    WIN.blit(num_food_text, (stats_x, 70))  # Position as needed
    WIN.blit(location_text, (stats_x, 100))  # Position as needed
    WIN.blit(conflicting_moves_text, (stats_x, 130))
    WIN.blit(in_motion_text, (stats_x, 160))