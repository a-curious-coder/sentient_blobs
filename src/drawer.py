import pygame


class Drawer:

    def __init__(self, WIN):
        self.WIN = WIN
        self.font = pygame.font.SysFont(None, 30)  # Adjust the size as needed

    def draw_lines(self, player, players, food):
        if food != None:
            for food_obj in food:
                pygame.draw.aaline(
                    surface=self.WIN,
                    color=(255, 255, 0, 100),
                    start_pos=(player.position.x, player.position.y),
                    end_pos=(food_obj.position.x, food_obj.position.y)
                )
        if players != None:
            for player_obj in players:
                pygame.draw.aaline(
                    surface=self.WIN,
                    color=(255, 0, 0, 100),
                    start_pos=(player.position.x, player.position.y),
                    end_pos=(player_obj.position.x, player_obj.position.y)
                )


    def draw_game(self, game_info_packet, players_list, food_list, quadtree=None, nearby_players = None, nearby_food = None):
        """Draw the game screen
        Arguments:
            players {list} -- A list of players
            food_list {list} -- A list of food items
        """
        game_info = game_info_packet.get_information()
        self.WIN.fill((0, 0, 0))
        # Background
        if quadtree != None:
            quadtree.draw(self.WIN)

        # Get highest score
        MAX_SCORE = max(player.score for player in players_list)

        for player in players_list:
            if not player.failed:
                player.set_colour(MAX_SCORE)
                player.draw(self.WIN)

        for food in food_list:
            food.draw(self.WIN)
        text_colour = (255, 255, 255)
        fps_text = self.font.render(f"FPS: {game_info['FPS']}", True, text_colour)
        score_text = self.font.render(f"Highest Score: {game_info['HIGH_SCORE']:.0f}", True, text_colour)
        generation_text = self.font.render(f"Generation: {game_info['GENERATION']}", True, text_colour)
        num_players_text = self.font.render(f"Players Remaining: {len(players_list)}", True, text_colour)
        
        minutes, seconds = divmod(game_info['GAME_TIME'], 60)
        timer_text = self.font.render(f"Time: {int(minutes)}:{int(seconds):02d}", True, text_colour)

        self.WIN.blit(timer_text, (10, 10))  # Position as needed
        self.WIN.blit(fps_text, (10, 40))  # Position as needed
        self.WIN.blit(score_text, (10, 70))  # Position as needed
        self.WIN.blit(num_players_text, (10, 100))  # Position as needed
        self.WIN.blit(generation_text, (10, 130))  # Position as needed

        # Find the selected player
        selected_player = next((player for player in players_list if player.selected), None)
        
        if selected_player:
            selected_player.vision_boundary.draw(self.WIN)
            # Draw stats for the selected player
            self.draw_player_stats(selected_player, game_info['SCREEN_WIDTH'])
            self.draw_lines(selected_player, nearby_players, nearby_food)

        pygame.display.flip()

    def draw_player_stats(self, selected_player, SCREEN_WIDTH):
        
        # Render the statistics text
        score_text = self.font.render(f"Score: {selected_player.score:.0f}", True, (255, 255, 255))
        players_eaten_text = self.font.render(f"Players Eaten: {selected_player.players_eaten}", True, (255, 255, 255))
        food_eaten_text = self.font.render(f"Food Consumed: {selected_player.food_eaten}", True, (255, 255, 255))
        location_text = self.font.render(f"Location: ({selected_player.position.x:.0f}, {selected_player.position.y:.0f})", True, (255, 255, 255))
        nn_outputs_text = self.font.render(f"Output: {round(selected_player.nn_outputs[0], 2)}", True, (255, 255, 255))
        radius_text = self.font.render(f"Radius: {selected_player.radius}", True, (255, 255, 255))  # Add radius text
        speed_text = self.font.render(f"Speed: {selected_player.speed:.2f}", True, (255, 255, 255))  # Add speed text
        angle_text = self.font.render(f"Angle: {selected_player.movement_angle:.0f}°", True, (255, 255, 255))  # Add speed text
        angle_input = self.font.render(f"NN: {selected_player.angle_input:.2f}", True, (255, 255, 255))  # Add speed text
        
        # Create a transparent card surface
        card_width = 300
        card_height = 300  # Increase card height to accommodate radius text
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
        card_surface.blit(nn_outputs_text, (text_x, text_y + 4.5 * text_spacing))
        card_surface.blit(radius_text, (text_x, text_y + 6 * text_spacing))  # Position radius text
        card_surface.blit(speed_text, (text_x, text_y + 7 * text_spacing))  # Position speed text
        card_surface.blit(angle_text, (text_x, text_y + 8 * text_spacing))  # Position angle text
        card_surface.blit(angle_input, (text_x, text_y + 9 * text_spacing))  # Position angle text
        
        # Position the card on the window
        card_x = SCREEN_WIDTH - card_width - 10
        card_y = 10
        self.WIN.blit(card_surface, (card_x, card_y))
