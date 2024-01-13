""" This module contains functions that handle game events. """
import os

import neat
import pygame


def quit_game(event, players):
    pygame.quit()
    quit()


def handle_keydown(event, players):
    if event.key == pygame.K_ESCAPE:
        pygame.quit()
        quit()


def handle_mousebuttondown(event, players):
    if event.button == 1:  # Left mouse button clicked
        mouse_x, mouse_y = pygame.mouse.get_pos()
        clicked_player = find_clicked_player(mouse_x, mouse_y, players)
        if clicked_player:
            clicked_player.selected = not clicked_player.selected
            deselect_other_players(clicked_player, players)


def find_clicked_player(mouse_x, mouse_y, players):
    for player in players:
        if (
            player.x - player.radius <= mouse_x <= player.x + player.radius
            and player.y - player.radius <= mouse_y <= player.y + player.radius
        ):
            return player
    return None


def deselect_other_players(clicked_player, players):
    for player in players:
        if player != clicked_player:
            player.selected = False

def handle_new_ai(event, players):
    if event.key == pygame.K_n:
        for player in players:
            player.ai = False
            player.failed = True
            player.fail_reason = "New AI"
        return True
    return False

def activity_detected(event, players):
    for filepath in event.file:
        _, ext = os.path.splitext(filepath)
        if ext == ".pkl":
            # Load the .pkl file into your neural network
            # ... your loading code here ...
            new_player_path = filepath
            with open(new_player_path, 'rb') as f:
                new_genome = pickle.load(f)
            config = neat.Config(neat.DefaultGenome, neat.DefaultReproduction,
                            neat.DefaultSpeciesSet, neat.DefaultStagnation,
                            "config-feedforward.txt")
            net = neat.nn.FeedForwardNetwork.create(winner_genome, config)
            players.append(
                Player(
                    random_x,
                    random_y,
                    f"Player {len(players_list)+1}",
                )
            )
            models_list.append(net)

            print(f"Loaded player model from {filepath}")
