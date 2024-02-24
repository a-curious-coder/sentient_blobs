import math
import os
import random
import sys

import pygame
from pygame.locals import *
from pygame.math import Vector2

import settings as settings
from src.assets import *
from src.quadtree import QuadTree
from src.utilities import get_colliding_particles

# Set random seed
random.seed(1)
# Initialize pygame
pygame.init()
font = pygame.font.SysFont(None, 30)

# Set up the screen
screen_width = 1000
screen_height = 1000
screen = pygame.display.set_mode((screen_width, screen_height))
pygame.display.set_caption("Quadtree Collision Detection")

# Create a quadtree
# boundary = pygame.Rect(0, 0, screen_width, screen_height)
boundary = Rectangle(Vector2(0, 0), Vector2(screen_width, screen_height))


# List to store players and food
players = []
foods = []
PLAYER_LIMIT = 10
FOOD_LIMIT = 750
NODE_CAPACITY = 1


def get_food():
    """Returns a list of n food items
    These are plotted within the game screen in locations where players aren't occupying.

    Args:
        n (int): The number of food items to generate.
        players (list): A list of Player objects.

    Returns:
        list: A list of n food items.
    """
    food_list = []

    for number in range(FOOD_LIMIT):
        while True:
            x = random.randint(0, screen_width)
            y = random.randint(0, screen_height)
            valid_position = True

            for player in players:
                if math.sqrt((x - player.position.x) ** 2 + (y - player.position.y) ** 2) <= player.radius + 20:
                    valid_position = False
                    break

            if valid_position:
                position = Vector2(x, y)
                game_object = Food(position, f"Food {number}")
                food_list.append(game_object)
                break

    return food_list


def get_players(n = 10):
    """Returns a list of n players
    These are plotted within the game screen in locations where players aren't occupying.

    Args:
        n (int): The number of players to generate.

    Returns:
        list: A list of n players.
    """
    players_list = []
    occupied_positions = set()

    for number in range(n):
        while True:
            x = random.randint(0, screen_width)
            y = random.randint(0, screen_height)
            valid_position = True

            for player in players_list:
                if math.sqrt((x - player.position.x) ** 2 + (y - player.position.y) ** 2) <= player.radius + 20:
                    valid_position = False
                    break

            if valid_position:
                new_player = Player(Vector2(x, y), number)
                new_player.set_colour((128, 128, 128))
                players_list.append(new_player)
                occupied_positions.add((x, y))
                break

    return players_list


def main():
    FPS = 1000
    clock = pygame.time.Clock()
    moveParticles = False
    showNames = True
    showQuadTree = False
    running = True
    followMouse = True
    quadtree = QuadTree(boundary, NODE_CAPACITY)
    use_quadtree = True
    sizes = settings.player["base_radius"]
    show_check_lines = False
    players = get_players(n=1)
    foods = get_food() 

    while running:
        for event in pygame.event.get():
            if event.type == QUIT:
                running = False
            elif event.type == MOUSEBUTTONDOWN:
                if event.button == 1:  # Left mouse button
                    player = Player(Vector2(pygame.mouse.get_pos()), len(players) + 1)
                    print(f"Adding player at {player.position}")
                    players.append(player)
            elif event.type == KEYUP:
                if event.key == K_ESCAPE:
                    running = False
                if event.key == K_SPACE:
                    moveParticles = not moveParticles
                if event.key == K_n:
                    showNames = not showNames
                    for player in players:
                        player.show_name = showNames
                if event.key == K_q:
                    showQuadTree = not showQuadTree
                if event.key == K_f:
                    use_quadtree = not use_quadtree
                if event.key == K_s:
                    show_check_lines = not show_check_lines

        clock.tick(FPS)
        collisions = 0
        eliminate_foods = []
        # Clear the screen
        screen.fill((0, 0, 0))

        # Draw fps
        fps = font.render(f"FPS: {int(clock.get_fps())}", True, (255, 255, 255))
        screen.blit(fps, (10, 30))

        # Draw number of players
        num_players = font.render(f"Players: {len(players)}", True, (255, 255, 255))
        screen.blit(num_players, (10, 50))

        quadtree = QuadTree(boundary, NODE_CAPACITY)

        if followMouse:
            players[0].position = Vector2(pygame.mouse.get_pos())

        for player in players:
            if player == players[0]:
                continue
            # Move the player randomly
            if moveParticles:
                player.move_randomly(screen)
            quadtree.insert(player)

        for food in foods:
            quadtree.insert(food)
        
        nearby_players = players
        nearby_food = foods

        # Check for collisions
        for player in players:
            
            if use_quadtree:
                nearby_players = quadtree.query(player.vision_boundary)
                nearby_food = quadtree.query(player.vision_boundary, object_type="Food")
            
            # ! Draw lines to nearby objects that are being checked for collisions with the player
            if show_check_lines:
                for p in nearby_players:
                    pygame.draw.line(screen, (255, 255, 255), player.position, p.position)
                for f in nearby_food:
                    pygame.draw.line(screen, (255, 0, 0), player.position, f.position)

            # ! Highlight colliding objects
            colliding_objects = get_colliding_particles(player, nearby_players)
            colliding_objects2 = get_colliding_particles(player, nearby_food)
            for o in colliding_objects:
                player.highlight()
                o.highlight(colour=(255,128,64))
                
            for o in colliding_objects2:
                player.highlight()
                o.highlight(colour=(255,0,0))
                
            player.draw(screen)
        
        for food in foods:
            food.draw(screen)                   

        # Draw num of collisions
        text = font.render(f"Collisions: {collisions}", True, (255, 255, 255))
        screen.blit(text, (10, 10))

        if showQuadTree:
            quadtree.draw(screen)
        
        # Update the display
        pygame.display.flip()

    # Quit pygame
    pygame.quit()


if __name__ == "__main__":
    main()
