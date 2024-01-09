import logging
import math
import random
import sys
import time
from math import floor, sqrt

import neat
import numpy as np
import pygame

from collision_logic import check_collision, player_eaten_player
from components.food import Food
from components.player import Player
from drawer import draw_stats
from game_event_handler import handle_keydown, handle_mousebuttondown, quit_game
from getters import *

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

pygame.init()

infoObject = pygame.display.Info()
w = infoObject.current_w
h = infoObject.current_h
SCREEN_WIDTH = w // 2
SCREEN_HEIGHT = h // 2
GAME_BORDER = 50
WIN = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))

FPS = 60  # Desired frames per second
SCORE_LIMIT = 200  # the maximum score of the game before we break the loop

# Game settings
MAX_SCORE = 0  # The highest score achieved by a player
NUM_FOOD = 250
ROUND_TIME = 30
FRAME_LIMIT = 600

# NEAT settings
MAX_GEN = 1000
GENERATION = 0
FOOD_DETECTION = 3
PLAYER_DETECTION = 3


# Can only eat other players if this player is at least this much bigger
EAT_PLAYER_THRESHOLD = 0.1


# Global settings
THRESHOLD_INACTIVITY = 3
PUNISHMENT_EATEN = 2
PUNISHMENT_INACTIVITY = 5
CONFLICTING_MOVES_PENALTY = 0.0015

def calculate_remaining_fitness(player_list: list, genomes_list):
    for player_index, player in enumerate(player_list):
        genomes_list[player_index].fitness = calculate_player_fitness(player)
    print("Round complete")


def calculate_player_fitness(player: Player) -> int:
    # Weights for each component
    weights = {
        "score": 1,
        "players_eaten": 1, # NOTE: Could have some influence on fitness later on
        "food_consumed": 1, # NOTE: Could have some influence on fitness later on
    }

    # Calculate the score for each component
    score_component = player.score * weights["score"]

    fitness_score = score_component

    if player.failed:
        fitness_score /= 2

    fitness_score = int(fitness_score - player.conflicting_moves_counter * CONFLICTING_MOVES_PENALTY)

    # Return the final fitness score
    return fitness_score


def conflicting_moves(keys) -> bool:
    return (keys[pygame.K_LEFT] and keys[pygame.K_RIGHT]) or \
        (keys[pygame.K_DOWN] and keys[pygame.K_UP])


def remove_element_from_lists(index, *args):
    if type(index) != int:
        print("Invalid type of index arg")
    for arg in args:
        arg.pop(index)

    
def process_player_collision(players_list, player):
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
    event_actions = {
        pygame.QUIT: quit_game,
        pygame.KEYDOWN: handle_keydown,
        pygame.MOUSEBUTTONDOWN: handle_mousebuttondown
    }

    for event in pygame.event.get():
        event_type = event.type
        if event_type in event_actions:
            event_actions[event_type](event, players)

    return players


def reduce_player_score(player):
    return player.score - (player.score * 0.002) if player.score > 1 else 0


def reduce_player_base_radius(player):
    return (
        player.base_radius - (player.base_radius * 0.001)
        if player.base_radius > 1
        else 1
    )


def end_generation(genomes_list, players_list, models_list):
    for i, player in enumerate(players_list):
        genomes_list[i].fitness = calculate_player_fitness(player)
        print(f"{player.name:^10}{genomes_list[i].fitness:^10}", end="")
        fitness_components = get_fitness_components(player)
        for key, value in fitness_components.items():
            value = round(value, 2)
            print(f"{value:^10}", end="")
        print(f"{player.fail_reason:<20}")
    print("Round time done")


def process_player_movement(player, output):
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

    # ! If any moves are True, check for conflicting moves
    player.conflicting_moves = False
    if any(keys):
        # Move player
        if conflicting_moves(keys):
            player.conflicting_moves = True
            player.conflicting_moves_counter += 1
            player.in_motion = False
        else:
            player.last_move_time = time.time()
            player.move(keys, SCREEN_WIDTH, SCREEN_HEIGHT)
            player.in_motion = True
    else:
        player.in_motion = False
    
    return player


def delete_player(player_index, players_list, genomes_list, models_list):
    player = players_list[player_index]

    # ! Set the fitness score
    genomes_list[player_index].fitness = calculate_player_fitness(player)

    # ! Print out the stats of the player to console
    fitness_components = get_fitness_components(player)
    print(f"{player.name:^10}{genomes_list[player_index].fitness:^10}", end="")
    for key, value in fitness_components.items():
        value = round(value, 2)
        print(f"{value:^10}", end="")
    print(f"{player.fail_reason:<20}")

    # ! Remove player, genome and model from the lists as we've modified the genome by reference (fucking hope I have)
    remove_element_from_lists(player_index, players_list, models_list, genomes_list)


def goal_reached(players_list):
    MAX_SCORE = max(player.score for player in players_list)
    return MAX_SCORE >= SCORE_LIMIT


def game_finished(players_list, end_round_time):
    return time.time() >= end_round_time or len(players_list) == 0 or goal_reached(players_list)


def add_score(player):
    if player.base_radius == 10: # TODO: Change this to a constant
        player.score += 1
    else:
        player.base_radius = player.base_radius + 1 if player.base_radius <= 9 else 10
    return player


def ensure_food(food_list, players_list):
    if len(food_list) < NUM_FOOD:
        food_needed = NUM_FOOD - len(food_list)
        food_list.extend(get_food(food_needed, players_list, SCREEN_WIDTH, SCREEN_HEIGHT))


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
        draw_stats(selected_player, WIN, SCREEN_WIDTH)

    pygame.display.flip()


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
    neat_components = get_neat_components(genomes, config, SCREEN_WIDTH, SCREEN_HEIGHT)
    players_list = neat_components["players"]
    genomes_list = neat_components["genomes"]
    models_list = neat_components["models"]

    food_list = get_food(NUM_FOOD, players_list, SCREEN_WIDTH, SCREEN_HEIGHT)

    game_running = True
    CURRENT_FRAME = 0
    # ! GAME LOOP
    while game_running:
        CURRENT_FRAME += 1
        print(CURRENT_FRAME)
        no_players = len(players_list) == 0
        if CURRENT_FRAME >= 600 or game_finished(players_list, end_round_time) or goal_reached(players_list) or no_players:
            end_generation(genomes_list, players_list, models_list)
            game_running = False
            continue

        players_list = check_for_game_events(players_list)

        GAME_TIME = round((pygame.time.get_ticks() - start_time) / 1000, 2)  # record the game time for this generation

        clock.tick(FPS)

        # Update player positions and check for collisions
        for player_index in reversed(range(len(players_list))):
            
            player = players_list[player_index]

            if player.failed:
                delete_player(player_index, players_list, genomes_list, models_list)
                continue

            process_player_collision(players_list , player)

            # ! Player punishments
            if player.score > 0:
                player.score = reduce_player_score(player)
            else:
                player.base_radius = reduce_player_base_radius(player)
                if player.base_radius <= 1:
                    player.failed = True
                    player.fail_reason += "player didn't eat enough food"

            # ! Gather inputs for player's genome
            inputs = get_inputs(player, players_list, food_list)

            # ! Get the output from the neural network
            output = models_list[player_index].activate(inputs)

            player = process_player_movement(player, output)
            
            if player.failed:
                delete_player(player_index, players_list, genomes_list, models_list)


        # ! Update food positions and check for collisions
        for food_item in food_list[
            :
        ]:  # Use a copy of the list to avoid issues with removing items during iteration
            for player in players_list:
                if check_collision(food_item, player):
                    player = add_score(player)
                    player.peak_score = max(player.score, player.peak_score)
                    player.food_consumed += 1
                    player.last_eaten_time = time.time()
                    food_list.remove(food_item)
                    break

        # ! Ensure there are always correct number of food items on the screen
        ensure_food(food_list, players_list)

        draw_game(players_list, food_list)



# Define a function to run NEAT algorithm to play flappy bird
def run_NEAT(config_file):
    
    # The template for the configuration file can be found here:
    #https://github.com/CodeReclaimers/neat-python/blob/master/examples/xor/config-feedforward
    # The description of the options in the configuration file can be found here:
    #https://neat-python.readthedocs.io/en/latest/config_file.html#defaultgenome-section
    
    # Use NEAT algorithm to build a neural network based on the pre-set configurtion
    # Create a neat.config.Config object from the configuration file
    config = neat.config.Config(neat.DefaultGenome, 
                                neat.DefaultReproduction,
                                neat.DefaultSpeciesSet, 
                                neat.DefaultStagnation,
                                config_file)
    
    config.genome_config.initial_connection = "full_nodirect"

    # Create a neat.population.Population object using the Config object created above
    neat_pop = neat.population.Population(config)
    
    # Show the summary statistics of the learning progress
    neat_pop.add_reporter(neat.StdOutReporter(True))
    stats = neat.StatisticsReporter()
    neat_pop.add_reporter(stats)
    
    # Call the run method on the Population object, giving it your fitness function and (optionally) the maximum number of generations you want NEAT to run
    neat_pop.run(main, MAX_GEN)
    
    # Get the most fit genome genome as our winner with the statistics.best_genome() function
    winner = stats.best_genome()
    
    # Show the final statistics
    print(f'\nBest genome:\n{winner}')



def main():
    config_file = 'config-feedforward.txt'
    run_NEAT(config_file)


if __name__ == "__main__":
    try:
        # Clear console
        print('\033c')
        main(config_file)
    except KeyboardInterrupt:
        print('\nUser quit the game!')
        quit()
