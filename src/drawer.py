import pygame


def draw_stats(selected_player, WIN, SCREEN_WIDTH):
    font = pygame.font.SysFont(None, 30)  # Adjust the size as needed
    
    # Render the statistics text
    score_text = font.render(f"Score: {selected_player.score:.0f}", True, (255, 255, 255))
    players_eaten_text = font.render(f"Players Eaten: {selected_player.players_eaten}", True, (255, 255, 255))
    food_eaten_text = font.render(f"Food Consumed: {selected_player.food_eaten}", True, (255, 255, 255))
    location_text = font.render(f"Location: ({selected_player.position.x:.0f}, {selected_player.position.y:.0f})", True, (255, 255, 255))
    conflicting_moves_text = font.render(f"Conflicting Moves: {selected_player.conflicting_moves}", True, (255, 255, 255))
    in_motion_text = font.render(f"In Motion: {selected_player.in_motion}", True, (255, 255, 255))
    radius_text = font.render(f"Radius: {selected_player.radius}", True, (255, 255, 255))  # Add radius text
    speed_text = font.render(f"Speed: {selected_player.speed}", True, (255, 255, 255))  # Add speed text
    # Create a transparent card surface
    card_width = 300
    card_height = 230  # Increase card height to accommodate radius text
    card_surface = pygame.Surface((card_width, card_height), pygame.SRCALPHA)
    card_surface.fill((255, 255, 255, 128))  # Transparent black background
    
    # Position the statistics text on the card
    text_x = 10
    text_y = 10
    text_spacing = 30
    card_surface.blit(score_text, (text_x, text_y))
    card_surface.blit(players_eaten_text, (text_x, text_y + text_spacing))
    card_surface.blit(food_eaten_text, (text_x, text_y + 2 * text_spacing))
    card_surface.blit(location_text, (text_x, text_y + 3 * text_spacing))
    card_surface.blit(conflicting_moves_text, (text_x, text_y + 4 * text_spacing))
    card_surface.blit(in_motion_text, (text_x, text_y + 5 * text_spacing))
    card_surface.blit(radius_text, (text_x, text_y + 6 * text_spacing))  # Position radius text
    card_surface.blit(speed_text, (text_x, text_y + 7 * text_spacing))  # Position speed text
    
    # Position the card on the window
    card_x = SCREEN_WIDTH - card_width - 10
    card_y = 10
    WIN.blit(card_surface, (card_x, card_y))
