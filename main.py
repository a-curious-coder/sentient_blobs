import logging
import math
import random
import sys
import time
from math import floor, sqrt

import neat
import numpy as np
import pygame

from components.food import Food
from components.player import Player

# Create a custom logger
logger = logging.getLogger(__name__)

# Set the level of the logger. This can be DEBUG, INFO, WARNING, ERROR, CRITICAL.
logger.setLevel(logging.ERROR)

# Create a console handler
ch = logging.StreamHandler()

# Create a formatter
formatter = logging.Formatter("[%(levelname)s]\t%(message)s")

# Add the formatter to the console handler
ch.setFormatter(formatter)

# Add the console handler to the logger
logger.addHandler(ch)

pygame.init()

infoObject = pygame.display.Info()
w = infoObject.current_w
h = infoObject.current_h
SCREEN_WIDTH = w // 2
SCREEN_HEIGHT = h // 2
GAME_BORDER = 50
WIN = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))

FPS = 30  # Desired frames per second
SCORE_LIMIT = 100  # the maximum score of the game before we break the loop


# Game settings
MAX_SCORE = 0  # The highest score achieved by a player
NUM_FOOD = 100
ROUND_TIME = 15
ITERATIONS = 1000

# NEAT settings
GENERATION = 0
FOOD_DETECTION = 3
PLAYER_DETECTION = 3

# Can only eat other players if this player is at least this much bigger
EAT_PLAYER_THRESHOLD = 0.1

# Global settings
THRESHOLD_INACTIVITY = 3
PUNISHMENT_EATEN = 2
PUNISHMENT_INACTIVITY = 5


def calculate_remaining_fitness( player_list, genomes_list):

    for player_index, player in enumerate(player_list):
        genomes_list[player_index].fitness = calculate_fitness(player)
    print("Round time done")

def correct_conflicting_movements(keys):
    keys[pygame.K_LEFT] = keys[pygame.K_LEFT] ^ keys[pygame.K_RIGHT]
    keys[pygame.K_DOWN] = keys[pygame.K_DOWN] ^ keys[pygame.K_UP]
    keys[pygame.K_UP] = keys[pygame.K_DOWN] ^ keys[pygame.K_UP]
    keys[pygame.K_RIGHT] = keys[pygame.K_LEFT] ^ keys[pygame.K_RIGHT]

def remove_element_from_lists( index, *args):
    if type(index) != int:
        print("Ivalid type of index arg")
    for arg in args:
        arg.pop(index)
    
def check_player_collision(players_list, player):
    colliding_players = [
                    other_player
                    for other_player in players_list
                    if player != other_player and check_collision(player, other_player)
                ]
    for colliding_player in colliding_players:
                    player_eaten_player(player, colliding_player)


def calculate_remaining_fitness( player_list, genomes_list):

    for player_index, player in enumerate(player_list):
        genomes_list[player_index].fitness = calculate_fitness(player)
    print("Round time done")

def correct_conflicting_movements(keys):
    keys[pygame.K_LEFT] = keys[pygame.K_LEFT] ^ keys[pygame.K_RIGHT]
    keys[pygame.K_DOWN] = keys[pygame.K_DOWN] ^ keys[pygame.K_UP]
    keys[pygame.K_UP] = keys[pygame.K_DOWN] ^ keys[pygame.K_UP]
    keys[pygame.K_RIGHT] = keys[pygame.K_LEFT] ^ keys[pygame.K_RIGHT]

def remove_element_from_lists( index, *args):
    if type(index) != int:
        print("Ivalid type of index arg")
    for arg in args:
        arg.pop(index)
    
def check_player_collision(players_list, player):
    colliding_players = [
                    other_player
                    for other_player in players_list
                    if player != other_player and check_collision(player, other_player)
                ]
    for colliding_player in colliding_players:
                    player_eaten_player(player, colliding_player)

def check_for_game_events(players):
    """Check for game events such as quitting or clicking on a player
    Arguments:
        players {list} -- A list of players

    Returns:
        list -- A list of players
    """
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            quit()
        # Person presses escape
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                pygame.quit()
                quit()
        elif (
            event.type == pygame.MOUSEBUTTONDOWN and event.button == 1
        ):  # Left mouse button clicked
            mouse_x, mouse_y = pygame.mouse.get_pos()
            # Check if the mouse click is within the bounding box of any player
            for player in players:
                if (
                    player.x - player.radius <= mouse_x <= player.x + player.radius
                    and player.y - player.radius <= mouse_y <= player.y + player.radius
                ):
                    # Invert the selected boolean
                    player.selected = not player.selected
                else:
                    player.selected = False
    return players

# An AI has played well enough to win
def goal_reached(players_list):
    MAX_SCORE = max(player.score for player in players_list)
    return MAX_SCORE >= SCORE_LIMIT

def game_finished(end_round_time, player_list):
    return time.time() >= end_round_time or len(player_list) == 0 or goal_reached(player_list)


def get_fitness_components(player):
    weights = {
        "peak_score": 1,
        "score": 1,
        "players_eaten": 1,
        "food_consumed": 1,
        "distance_travelled": 1,
    }

    return {
        "peak_score": player.peak_score * weights["peak_score"],
        "score": player.score * weights["score"],
        "players_eaten": player.players_eaten * weights["players_eaten"],
        "food_consumed": player.food_consumed * weights["food_consumed"],
        "distance_travelled": int(
            player.distance_travelled * weights["distance_travelled"]
        ),
    }

def calculate_fitness(player):
    # Weights for each component
    weights = {
        "peak_score": 0.5,
        "score": 1,
        "players_eaten": 1,
        "food_consumed": 1,
        "distance_travelled": 0.3,
    }
    # Calculate the score for each component
    score_component = player.score * weights["score"]

    fitness_score = score_component

    if player.failed:
        fitness_score /= 2

    fitness_score = int(fitness_score - player.conflicting_moves_counter * CONFLICTING_MOVES_PENALTY)

    # Return the final fitness score
    return fitness_score

def reduce_player_score(player):
    return player.score - (player.score * 0.002) if player.score > 1 else 0

def reduce_player_base_radius(player):
    return (
        player.base_radius - (player.base_radius * 0.001)
        if player.base_radius > 1
        else 1
    )

def game_finished(players_list, end_round_time):
    return time.time() >= end_round_time or len(players_list) < 2

def end_generation(genomes_list, players_list, models_list):
    for i, player in enumerate(players_list):
        genomes_list[i].fitness = calculate_fitness(player)
        print(f"{player.name:^10}{genomes_list[i].fitness:^10}", end="")
        fitness_components = get_fitness_components(player)
        for key, value in fitness_components.items():
            value = round(value, 2)
            print(f"{value:^10}", end="")
        print(f"{player.fail_reason:<20}")
    print("Round time done")

def evaluate_genomes(genomes, config):
    """Evaluate the fitness of each genome in the genomes list
    Arguments:
        genomes {list} -- A list of genomes
        config {neat.config} -- The NEAT configuration file
    """
    global SCREEN_WIDTH, SCREEN_HEIGHT, GENERATION, GAME_TIME, WIN  # use the global variable gen and SCREEN

    print(f"{'Name':^10}{'Fitness':^10}{'Peak':^10}{'Score':^10}{'p_eaten':^10}{'f_eaten':^10}{'Distance':^10}{'Death Reason':<20}")

    GENERATION += 1  # update the generation

    # Calculate game's end time from now
    end_round_time = ROUND_TIME + time.time()
    clock = pygame.time.Clock()  # Create a clock object
    start_time = (
        pygame.time.get_ticks()
    )  # reset the start_time after every time we update our generation

    # ! Get the neat components
    neat_components = get_neat_components(genomes, config)

    players_list = neat_components["players"]
    genomes_list = neat_components["genomes"]
    models_list = neat_components["models"]
    food_list = get_food(NUM_FOOD)

    while True:
        if game_finished(end_round_time, players_list):
            calculate_remaining_fitness(players_list, genomes_list)
            break

        # Continue the game loop
        players_list = check_for_game_events(players_list)

        GAME_TIME = round(
            (pygame.time.get_ticks() - start_time) / 1000, 2
        )  # record the game time for this generation

        clock.tick(FPS)

        keys = {
            pygame.K_LEFT: False,
            pygame.K_RIGHT: False,
            pygame.K_UP: False,
            pygame.K_DOWN: False,
        }

    key_mapping = {
        0: {pygame.K_LEFT},
        1: {pygame.K_RIGHT},
        2: {pygame.K_UP},
        3: {pygame.K_DOWN},
    }

    # Calculate game's end time from now
    end_round_time = ROUND_TIME + time.time()
    clock = pygame.time.Clock()  # Create a clock object
    start_time = (pygame.time.get_ticks())  # reset the start_time after every time we update our generation

    # ! Get the neat components
    neat_components = get_neat_components(genomes, config)

    players_list = neat_components["players"]
    genomes_list = neat_components["genomes"]
    models_list = neat_components["models"]
    food_list = get_food(NUM_FOOD, players_list)
    game_running = True
    # ! GAME LOOP
    while game_running:
        no_players = len(players_list) == 0

        if game_finished(players_list, end_round_time) or goal_reached(players_list) or no_players:
            end_generation(genomes_list, players_list, models_list)
            game_running = False
            continue

        players_list = check_for_game_events(players_list)

        GAME_TIME = round((pygame.time.get_ticks() - start_time) / 1000, 2)  # record the game time for this generation

        clock.tick(FPS)

        delete_player = False

        # Update player positions and check for collisions
        for player_index in reversed(range(len(players_list))):
            player = players_list[player_index]
            delete_player = player.failed
            if not delete_player:

                # ! Player punishments
                if player.score > 0:
                    player.score = reduce_player_score(player)
                else:
                    player.base_radius = reduce_player_base_radius(player)
                    if player.base_radius <= 1:
                        player.failed = True
                        player.fail_reason += "player didn't eat enough food"

                # ! Player genome (neural network) inputs
                inputs = get_inputs(player, players_list, food_list)

                # Get neural network output
                output = models_list[player_index].activate(inputs)

                # Convert the output to probabilities of which choice it's making
                probabilities = np.exp(output) / np.sum(np.exp(output))

                # Choose the action with the highest probability
                # NOTE: A single action could select multiple moves as some values represent pairs of simultaneous moves
                max_probability = np.max(probabilities)
                max_indices = np.where(probabilities == max_probability)[0]
                actions = max_indices.tolist()
                ai_chosen_moves = []
                for action in actions:
                    # Map the action to corresponding key press(es)
                    ai_chosen_moves += key_mapping[action]

                # Map the action to key press(es)
                for key in keys:
                    keys[key] = key in ai_chosen_moves

                conflicting_moves = False
                # ! If any moves are True, check for conflicting moves
                if any(keys):
                    # Move player
                    correct_conflicting_movements(keys)
                    player.last_move_time = time.time()
                    player.move(keys, SCREEN_WIDTH, SCREEN_HEIGHT)
                    player.in_motion = True
                else:
                    player.in_motion = False
                    player.conflicting_moves_counter += 1
                    player.player_still = True

                if player.player_still:
                    # Increment the timer for how long the player has been still
                    player.still_counter += time.time() - player.last_move_time

                # ! Reset keys for next player
                for key in keys:
                    keys[key] = False

            if not delete_player:
                check_player_collision(players_list , player)

            else:
                # Set the fitness score
                genomes_list[player_index].fitness = calculate_fitness(player)
                fitness_components = get_fitness_components(player)
                # ! PRINT STATS

                print(
                    f"{player.name:^10}{genomes_list[player_index].fitness:^10}", end=""
                )
                for key, value in fitness_components.items():
                    value = round(value, 2)
                    print(f"{value:^10}", end="")
                print(f"{player.fail_reason:<20}")
                # Set the player as failed
                players_list[player_index].failed = True
                # Remove them from the lists as we've modified the genome by reference (fucking hope I have)
                players_list.pop(player_index)
                models_list.pop(player_index)
                genomes_list.pop(player_index)

        # ! Update food positions and check for collisions
        for food_item in food_list[
            :
        ]:  # Use a copy of the list to avoid issues with removing items during iteration
            for player in players_list:
                if check_collision(food_item, player):
                    player = increment_score(player)
                    player.peak_score = max(player.score, player.peak_score)
                    player.food_consumed += 1
                    player.last_eaten_time = time.time()
                    food_list.remove(food_item)
                    break

        # Ensure there are always correct number of food items on the screen
        ensure_food(food_list, players_list)

        draw_game(players_list, food_list)

def increment_score(player):
    if player.base_radius == 10: # TODO: Change this to a constant
        player.score += 1
    else:
        player.base_radius = player.base_radius + 1 if player.base_radius <= 9 else 10
    return player

def ensure_food(food_list, players_list):
    if len(food_list) < NUM_FOOD:
        food_needed = NUM_FOOD - len(food_list)
        food_list.extend(get_food(food_needed, players_list))

def draw_game(players_list, food_list):
    """Draw the game screen
    Arguments:
        players {list} -- A list of players
        food_list {list} -- A list of food items
    """
    # Background
    WIN.fill((0, 0, 0))

    # Get highest score
    MAX_SCORE = max(player.score for player in players_list)

    for player in players_list:
        # Set colour between red and green based on score (0, max_score)
        # 0 = red, max_score = green
        # 0 = 255, max_score = 0
        color = (255, 0, 0)
        if MAX_SCORE > 0:
            color = (
                255 - int(player.score / MAX_SCORE * 255),
                int(player.score / MAX_SCORE * 255),
                0,
            )
        player.color = color
        player.draw(WIN)

    for food in food_list:
        food.draw(WIN)

    # Initialize the font module
    pygame.font.init()

    # Render the scores as text
    font = pygame.font.SysFont(None, 30)  # Adjust the size as needed
    score_text = font.render(
        f"Highest Score: {MAX_SCORE:.0f}", True, (255, 255, 255)
    )  # White text
    num_players_text = font.render(
        f"Players Remaining: {len(players_list)}", True, (255, 255, 255)
    )  # White text
    generation_text = font.render(f"Generation: {GENERATION}", True, (255, 255, 255))
    minutes, seconds = divmod(GAME_TIME, 60)
    timer_text = font.render(
        f"Time: {int(minutes)}:{int(seconds):02d}", True, (255, 255, 255)
    )
    WIN.blit(timer_text, (10, 100))  # Position as needed
    # Draw the scores onto the screen
    WIN.blit(score_text, (10, 10))  # Position as needed
    WIN.blit(num_players_text, (10, 40))  # Position as needed
    WIN.blit(generation_text, (10, 70))

    # Find the selected player
    selected_player = next((player for player in players_list if player.selected), None)

    if selected_player:
        # Draw lines to the 10 nearest foods to the selected player
        player_x = selected_player.x
        player_y = selected_player.y
        food_distances = calculate_and_sort_player_distances(selected_player, food_list)
        nearest_food = list(food_distances.items())[:FOOD_DETECTION]
        for food_name, _ in nearest_food:
            food_obj = next((obj for obj in food_list if obj.name == food_name), None)
            if food_obj:
                pygame.draw.aaline(
                    WIN,
                    (0, 255, 0, 100),
                    (player_x, player_y),
                    (food_obj.x, food_obj.y),
                    2,
                )

        # Draw lines to the 10 nearest players to the selected player
        player_distances = calculate_and_sort_player_distances(selected_player, players_list)
        nearest_players = list(player_distances.items())[:PLAYER_DETECTION]
        for player_name, _ in nearest_players:
            other_player = next(
                (obj for obj in players_list if obj.name == player_name), None
            )
            if other_player:
                pygame.draw.aaline(
                    WIN,
                    (255, 0, 0, 100),
                    (player_x, player_y),
                    (other_player.x, other_player.y),
                    2,
                )
        # Draw stats for the selected player
        font = pygame.font.SysFont(None, 30)  # Adjust the size as needed
        score_text = font.render(
            f"Score: {selected_player.score:.0f}", True, (255, 255, 255)
        )  # White text
        num_players_text = font.render(
            f"Players Eaten: {selected_player.players_eaten}", True, (255, 255, 255)
        )
        num_food_text = font.render(
            f"Food Consumed: {selected_player.food_consumed}", True, (255, 255, 255)
        )
        location_text = font.render(
            f"Location: ({selected_player.x:.0f}, {selected_player.y:.0f})",
            True,
            (255, 255, 255),
        )
        conflicting_moves_text = font.render(
            f"Conflicting Moves: {selected_player.conflicting_moves}",
            True,
            (255, 255, 255),
        )
        in_motion_text = font.render(
            f"In Motion: {selected_player.in_motion}", True, (255, 255, 255)
        )
        stats_x = SCREEN_WIDTH - 300
        WIN.blit(score_text, (stats_x, 10))  # Position as needed
        WIN.blit(num_players_text, (stats_x, 40))  # Position as needed
        WIN.blit(num_food_text, (stats_x, 70))  # Position as needed
        WIN.blit(location_text, (stats_x, 100))  # Position as needed
        WIN.blit(conflicting_moves_text, (stats_x, 130))
        WIN.blit(in_motion_text, (stats_x, 160))

    pygame.display.flip()

# ! COLLISION LOGIC
def check_collision(obj1, obj2) -> bool:
    """Check if two objects are colliding
    NOTE: For food and players use only... for now
    Arguments:
        obj1 {object} -- First object
        obj2 {object} -- Second object
    """
    dx = obj1.x - obj2.x
    dy = obj1.y - obj2.y
    distance = math.sqrt(dx * dx + dy * dy)
    threshold = obj1.radius + (obj1.radius * 0.1) + obj2.radius
    return distance <= threshold

def player_eaten_player(player, colliding_player):
    # ! this player ate other player
    if floor(player.radius) > floor(colliding_player.radius * 1.1):
        if player.score != 0:
            player.score += colliding_player.radius
        else:
            player.base_radius += colliding_player.base_radius
            if player.base_radius > 10:
                player.score = player.base_radius - 10
                player.base_radius = 10
        player.peak_score = max(player.score, player.peak_score)
        player.players_eaten += 1
        player.last_eaten_time = time.time()
        colliding_player.failed = True
        colliding_player.fail_reason += f"eaten by {player.name} at {player.score}"

def handle_wall_collision(player):
    if collide_with_wall(player):
        return True
    return False

def collide_with_wall(player):
    if player.x + player.radius >= SCREEN_WIDTH or player.x - player.radius <= 0:
        return True
    if player.y + player.radius >= SCREEN_HEIGHT or player.y - player.radius <= 0:
        return True
    return False

# ! GETTERS
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
        [player.score, player.radius, player.x, player.y]
        + player_distances
        + player_sizes
        + food_distances
    )

    return inputs

def get_distance_to_walls(player):
    x0 = player.x
    y0 = player.y
    r = player.radius
    L = 0
    R = SCREEN_WIDTH
    T = 0
    B = SCREEN_HEIGHT
    # Calculate distances to each edge
    distance_left = abs(x0 - L) - r
    distance_top = abs(y0 - T) - r
    distance_right = abs(x0 - R) - r
    distance_bottom = abs(y0 - B) - r

    # Ensure all distances are positive
    distance_left = max(0, distance_left)
    distance_top = max(0, distance_top)
    distance_right = max(0, distance_right)
    distance_bottom = max(0, distance_bottom)

    # Return the smallest distance
    return [distance_left, distance_top, distance_right, distance_bottom]

def calculate_and_sort_player_distances(player, players):
    distances = {}
    for other_player in players:
        if other_player != player:
            dx = other_player.x - player.x
            dy = other_player.y - player.y
            distance = sqrt(dx * dx + dy * dy)
            
            # Ensure the distance is always positive
            distance = max(distance - 2 * min(player.radius, other_player.radius), 0)
            
            distances[other_player.name] = distance

    # Sort the dictionary by values (distances)
    sorted_distances = dict(sorted(distances.items(), key=lambda item: item[1]))

    # If there aren't 10 players, fill the remaining slots with 9999
    while len(sorted_distances) < 10:
        sorted_distances[f"Player_{len(sorted_distances)+1}"] = 9999

    # Get the nearest 10 players
    return dict(sorted(sorted_distances.items(), key=lambda item: item[1])[:10])

def get_nearest_players_sizes(player, players):
    # Assuming calculate_and_sort_player_distances function is available
    nearest_players = calculate_and_sort_player_distances(player, players)

    # Create a dictionary to store the sizes of the nearest players
    sizes = {}

    # Iterate through the nearest players
    for other_player in players:
        # Check if the other player is in the list of nearest players
        if other_player.name in nearest_players:
            # Add the player's size (radius) to the dictionary
            sizes[other_player.name] = other_player.radius

    while len(sizes) < 10:
        sizes[f"FillerValue_{len(sizes)+1}"] = 0
    # Return the dictionary
    return sizes

def get_neat_components(genomes, config) -> dict:
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

    for _, genome in genomes:  # Replace 10 with the desired number of players
        players_list.append(
            Player(
                random.randint(GAME_BORDER, SCREEN_WIDTH - GAME_BORDER),
                random.randint(GAME_BORDER, SCREEN_HEIGHT - GAME_BORDER),
                f"Player {len(players_list)+1}",
            )
        )
        # Initialize the fitness score to 0
        genome.fitness = 0
        genomes_list.append(genome)
        # Create a neural network for each genome
        model = neat.nn.FeedForwardNetwork.create(
            genome, config
        )  # Set up the neural network for each genome using the configuration we set
        models_list.append(model)  # Append the neural network in the list

    # Return a dictionary of lists
    return {"players": players_list, "genomes": genomes_list, "models": models_list}

def get_food(n: int, players: list) -> list:
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

    for number in range(n):
        while True:
            x = random.randint(GAME_BORDER, SCREEN_WIDTH - GAME_BORDER)
            y = random.randint(GAME_BORDER, SCREEN_HEIGHT - GAME_BORDER)
            valid_position = True

            for player in players:
                if math.sqrt((x - player.x) ** 2 + (y - player.y) ** 2) <= player.radius:
                    valid_position = False
                    break

            if valid_position:
                food_list.append(Food(x, y, f"Food {number}"))
                occupied_positions.add((x, y))
                break

    return food_list

def main():
    print(
        "Yes... This is the main function to main.py file... Try running neat-ai.py instead"
    )
    return 0

if __name__ == "__main__":
    sys.exit(main())