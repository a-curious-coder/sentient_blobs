""" This module contains functions that handle game events. """
import math
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
        distance = math.sqrt((mouse_x - player.position.x)**2 + (mouse_y - player.position.y)**2)
        if distance <= player.radius:
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
