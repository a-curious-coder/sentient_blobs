""" This module contains functions that handle game events. """
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
            player.x - player.value <= mouse_x <= player.x + player.value
            and player.y - player.value <= mouse_y <= player.y + player.value
        ):
            return player
    return None


def deselect_other_players(clicked_player, players):
    for player in players:
        if player != clicked_player:
            player.selected = False
