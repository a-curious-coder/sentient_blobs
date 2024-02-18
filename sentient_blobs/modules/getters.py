""" This file contains functions that are used to get data from the game. """
import math
import random

import modules.neat
import modules.settings as settings
import pygame
from modules.components.food import Food
from modules.components.player import Player
from pygame.math import Vector2

GAME_BORDER = settings.game["padding"]
FOOD_DETECTION = settings.player["food_detection"]
PLAYER_DETECTION = settings.player["player_detection"]

def get_inputs(player, players_list, food_list):
    player_distances = list(
        calculate_and_sort_player_distances(player, players_list).values()
    )[:PLAYER_DETECTION]

    player_sizes = list(
        get_nearest_players_sizes(player, players_list).values()
    )[:PLAYER_DETECTION]

    food_distances = list(
        calculate_and_sort_player_distances(player, food_list).values()
    )[:FOOD_DETECTION]

    # Convert the collected data to a format the neural network will recognise
    inputs = tuple(
        [player.score, player.radius, player.position.x, player.position.y]
        + player_distances
        + player_sizes
        + food_distances
    )

    return inputs


def calculate_and_sort_player_distances(player, players):
    distances = {}
    count = 0
    for other_player in players:
        if other_player != player:
            dx = other_player.position.x - player.position.x
            dy = other_player.position.y - player.position.y
            distance = math.sqrt(dx * dx + dy * dy)
            
            # Ensure the distance is always positive
            distance = max(distance - 2 * min(player.radius, other_player.radius), 0)
            
            distances[other_player.name] = distance
        count += 1

    # Sort the dictionary by values (distances)
    sorted_distances = dict(sorted(distances.items(), key=lambda item: item[1]))

    # If there aren't 10 players, fill the remaining slots with 9999
    while len(sorted_distances) < 10:
        placeholder_name = f"PlaceholderPlayer{len(sorted_distances) +  1}"
        sorted_distances[placeholder_name] = 9999
        count += 1

    # Get the nearest 10 players
    return dict(sorted(sorted_distances.items(), key=lambda item: item[1])[:10])


def get_nearest_players_sizes(player, players):
    # Assuming calculate_and_sort_player_distances function is available
    nearest_players = calculate_and_sort_player_distances(player, players)

    # Create a dictionary to store the sizes of the nearest players
    sizes = {}

    count = 0
    # Iterate through the nearest players
    for other_player in players:
        # Check if the other player is in the list of nearest players
        if other_player.name in nearest_players:
            # Add the player's size (radius) to the dictionary
            sizes[other_player.name] = other_player.radius
        count += 1

    while len(sizes) < 10:
        sizes[f"FillerValue_{len(sizes)+1}"] = 0
        count += 1
    # Return the dictionary
    return sizes


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
    random.seed(42)
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

        players_list.append(
            Player(
                Vector2(random_x,
                random_y),
                len(players_list)+1,
            )
        )

        # Initialize the fitness score to 0
        genome.fitness = 0
        genomes_list.append(genome)
        # Create a neural network for each genome
        model = modules.neat.nn.FeedForwardNetwork.create(
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
