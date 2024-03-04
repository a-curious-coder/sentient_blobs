""" This module contains functions that handle game events. """
import math
import os

import pygame

PAUSED = False

def check_for_game_events(players):
    """Check for game events such as quitting or clicking on a player
    Arguments:
        players {list} -- A list of players

    Returns:
        list -- A list of players
    """
    global PAUSED
    event_actions = {
        pygame.MOUSEBUTTONDOWN: handle_mousebuttondown
    }

    for event in pygame.event.get():
        event_type = event.type
        if event_type in event_actions:
            event_actions[event_type](event, players)
        if event_type == pygame.KEYDOWN:
            if event.key == pygame.K_SPACE:
                PAUSED = not PAUSED
                pause(players)
            if event.key == pygame.K_ESCAPE:
                quit_game()

def pause(players):
    # TODO: Work on pause functionality
    while PAUSED:
        check_for_game_events(players)
        continue

def quit_game():
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
