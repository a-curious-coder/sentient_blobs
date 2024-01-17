import math
import random

import pygame
from components.food import Food
from components.player import Player
from components.utilities.quadtree import QuadTree
from pygame.locals import *

# Initialize pygame
pygame.init()

# Set up the screen
screen_width = 800
screen_height = 600
screen = pygame.display.set_mode((screen_width, screen_height))
pygame.display.set_caption("Quadtree Collision Detection")

# Create a quadtree
boundary = pygame.Rect(0, 0, screen_width, screen_height)
quadtree = QuadTree(boundary, 2)

# List to store players and food
players = []
foods = []

def get_food(quadtree):
    """Returns a list of n food items
    These are plotted within the game screen in locations where players aren't occupying.

    Args:
        n (int): The number of food items to generate.
        players (list): A list of Player objects.

    Returns:
        list: A list of n food items.
    """
    food_list = []
    occupied_positions = set([(player.x, player.y) for player in players])

    for number in range(100):
        while True:
            x = random.randint(0, screen_width)
            y = random.randint(0, screen_height)
            valid_position = True

            for player in players:
                if math.sqrt((x - player.x) ** 2 + (y - player.y) ** 2) <= player.radius + 20:
                    valid_position = False
                    break

            if valid_position:
                food_list.append(Food(x, y, f"Food {number}"))
                occupied_positions.add((x, y))
                quadtree.insert(food_list[-1])
                break

    return food_list

def get_players(quadtree):
    """Returns a list of n players
    These are plotted within the game screen in locations where players aren't occupying.

    Args:
        n (int): The number of players to generate.

    Returns:
        list: A list of n players.
    """
    players_list = []
    occupied_positions = set()

    for number in range(10):
        while True:
            x = random.randint(0, screen_width)
            y = random.randint(0, screen_height)
            valid_position = True

            for player in players_list:
                if math.sqrt((x - player.x) ** 2 + (y - player.y) ** 2) <= player.radius + 20:
                    valid_position = False
                    break

            if valid_position:
                players_list.append(
                    Player(
                        x,
                        y,
                        f"Player {number}",
                    )
                )
                occupied_positions.add((x, y))
                quadtree.insert(players_list[-1])
                break

    return players_list


def main():
    running = True
    # foods = get_food(quadtree)
    players = get_players(quadtree)
    while running:
        for event in pygame.event.get():
            if event.type == QUIT:
                running = False
            elif event.type == MOUSEBUTTONDOWN:
                if event.button == 1:  # Left mouse button
                    x, y = pygame.mouse.get_pos()
                    player = Player(x, y, len(players) + 1)
                    # Generate random value between 1 and 10
                    random_value = random.randint(1, 10)
                    # Set the player's radius to the random value
                    player.add_to_score(random_value)
                    players.append(player)
                    quadtree.insert(player)  # Insert player position into quadtree

        # Clear the screen
        screen.fill((0, 0, 0))
        quadtree.draw(screen)
        # Update and draw players
        for player in players:
            player.draw(screen)

        for food in foods:
            food.draw(screen)

        collisions = 0
        # Check for collisions
        for player in players:
            range = pygame.Rect(player.x - player.radius, player.y - player.radius, player.radius * 2, player.radius * 2)
            collided_circles = quadtree.query(range)
            # draw the range
            pygame.draw.rect(screen, (255, 255, 255), range, 1)

            for circle in collided_circles:
                if player != circle:
                    if player.collides_with(circle):
                        collisions += 1
                        player.set_colour((0, 255, 0))
                        circle.set_colour((0, 255, 0))

        # Draw num of collisions
        font = pygame.font.SysFont("Arial", 18)
        text = font.render(f"Collisions: {collisions}", True, (255, 255, 255))
        screen.blit(text, (10, 10))
        
        # Update the display
        pygame.display.flip()

    # Quit pygame
    pygame.quit()

if __name__ == "__main__":
    main()
