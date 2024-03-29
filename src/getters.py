""" This file contains functions that are used to get data from the game. """
import math
import random

import pygame
from pygame.math import Vector2

import settings

from .assets import Food, Player
from .neat import *

GAME_BORDER = settings.game["padding"]
FOOD_DETECTION = settings.player["food_detection"]
PLAYER_DETECTION = settings.player["player_detection"]

def get_inputs(player, players_list, food_list):
    # TODO: Refactor this for better readability
    player_detections = list(get_nearest_particle_distances(player, players_list).values())
    player_distances = [p[0] for p in player_detections]
    player_bools = [p[1] for p in player_detections]
    food_distances = [p[0] for p in list(get_nearest_particle_distances(player, food_list).values())]

    # Convert the collected data to a format the neural network will recognise
    inputs = tuple(
        [player.position.x, player.position.y]
        + player_distances
        + player_bools
        + food_distances
    )

    return inputs


# Create a function that measures the distance between the_player and each player in the list from the edge of the_player's circle to the edge of the other player's circle
# This function will be used to determine the nearest players to the_player
def get_nearest_particle_distances(the_player, players):
    distances = {}
    for other_player in players:
        if other_player != the_player:
            dx = other_player.position.x - the_player.position.x
            dy = other_player.position.y - the_player.position.y
            distance = math.sqrt(dx * dx + dy * dy)
            
            # Calculate the distance from the edge of their radius
            distance_from_edge = distance - (the_player.radius + other_player.radius)
            
            # Ensure the distance is always positive
            distance_from_edge = max(distance_from_edge,  0)
            
            distances[other_player.name] = (distance_from_edge, the_player.radius > other_player.radius)

    # Sort the dictionary by values (distances)
    sorted_distances = dict(sorted(distances.items(), key=lambda item: item[1][0]))
    
    # If there aren't  PLAYER_DETECTION players, fill the remaining slots with  9999
    while len(sorted_distances) <  PLAYER_DETECTION:
        placeholder_name = f"PlaceholderPlayer{len(sorted_distances) +   1}"
        sorted_distances[placeholder_name] =  (9999, 0)

    # Get the nearest  PLAYER_DETECTION players
    return dict(sorted(sorted_distances.items(), key=lambda item: item[1])[:PLAYER_DETECTION])


def get_neat_components(genomes, config, w, h) -> dict:
    """Returns a dictionary of lists.

    The lists contain the players, genomes, and models for each player.

    Arguments:
        genomes {list} -- A list of genomes.
        config {neat.config} -- The NEAT configuration file.

    Returns:
        dict -- A dictionary of lists.
    """
    players_list = []
    genomes_list = []
    models_list = []
    #  Set seed for reproducibility
    # random.seed(42)
    counter = 0
    for _, genome in genomes:  # Replace 10 with the desired number of players
        random_x = random.randint(GAME_BORDER, w - GAME_BORDER)
        random_y = random.randint(GAME_BORDER, h - GAME_BORDER)
        # Check if the random position is within the radius of any other player
        while any(
            [
                math.sqrt((random_x - player.position.x) ** 2 + (random_y - player.position.y) ** 2)
                <= player.radius
                for player in players_list
            ]
        ):
            random_x = random.randint(GAME_BORDER, w - GAME_BORDER)
            random_y = random.randint(GAME_BORDER, h - GAME_BORDER)

        
        # Initialize the fitness score to 0
        genome.fitness = 0
        genomes_list.append(genome)

        players_list.append(
            Player(
                Vector2(random_x,
                random_y),
                counter,
            )
        )
        counter += 1    

        # Create a neural network for each genome
        model = nn.create(
            genome, config
        )  # Set up the neural network for each genome using the configuration we set
        models_list.append(model)  # Append the neural network in the list

    # Return a dictionary of lists
    return {"players": players_list, "genomes": genomes_list, "models": models_list}


def get_food(n: int, players: list, w, h) -> list:
    """Returns a list of n food items
    These are plotted within the game screen in locations where players aren't occupying.

    Args:
        n (int): The number of food items to generate.
        players (list): A list of Player objects.

    Returns:
        list: A list of n food items.
    """
    food_list = []
    occupied_positions = set([(player.position.x, player.position.y) for player in players])

    for number in range(n):
        while True:
            x = random.randint(GAME_BORDER, w - GAME_BORDER)
            y = random.randint(GAME_BORDER, h - GAME_BORDER)
            valid_position = True

            for player in players:
                if math.sqrt((x - player.position.x) ** 2 + (y - player.position.y) ** 2) <= player.radius + 20:
                    valid_position = False
                    break

            if valid_position:
                food_list.append(Food(Vector2(x, y), number))
                occupied_positions.add((x, y))
                break

    return food_list


def get_fitness_components(player):
    weights = {
        "peak_score": 1,
        "score": 1,
        "players_eaten": 1,
        "food_eaten": 1,
        "distance_travelled": 1,
    }

    return {
        "peak_score": player.peak_score * weights["peak_score"],
        "score": player.score * weights["score"],
        "players_eaten": player.players_eaten * weights["players_eaten"],
        "food_eaten": player.food_eaten * weights["food_eaten"],
        "distance_travelled": int(
            player.distance_travelled * weights["distance_travelled"]
        ),
    }
