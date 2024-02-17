import asyncio
import cProfile
import math
import pickle
import random
import re
import sys
import time
from math import floor, sqrt

import neat
import numpy as np
import pygame
import settings
from collision_logic import check_collision, player_eaten_player
from components.food import Food
from components.player import Player
from components.utilities.quadtree import QuadTree
from drawer import draw_stats
from game_event_handler import handle_keydown, handle_mousebuttondown, quit_game
from getters import *
from components.utilities.boundary_shape import Rectangle
# Import clock
from pygame import time as pytime

cProfile.run('re.compile("foo|bar")')

pygame.init()
PAUSED = False
infoObject = pygame.display.Info()
w = infoObject.current_w
h = infoObject.current_h
SCREEN_WIDTH = w // 2
SCREEN_HEIGHT = h // 2
WIN = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))

GAME_PADDING = settings.game["padding"]
FPS = settings.game["fps"]
NUM_FOOD = settings.game["num_food"]

SCORE_LIMIT = 200  # the maximum score of the game before we break the loop

# Game settings
MAX_SCORE = 0  # The highest score achieved by a player
CALCULATIONS = 0

# NEAT settings
GENERATION = 0
MAX_GEN = settings.neat["max_gen"]
FOOD_DETECTION = settings.player["food_detection"]
PLAYER_DETECTION = settings.player["player_detection"]
SCORE_REDUCTION = settings.player["score_reduction"]

# Can only eat other players if this player is at least this much bigger
EAT_PLAYER_THRESHOLD = settings.player["eat_player_threshold"]
CONFLICTING_MOVES_PENALTY = 0.0015


def calculate_remaining_fitness(player_list: list, genomes_list):
    for player_index, player in enumerate(player_list):
        genomes_list[player_index].fitness = calculate_player_fitness(player)
    print("Round complete")


def paused():
    # Display a "Paused" message
    largeText = pygame.font.SysFont("comicsansms",  115)
    TextSurf, TextRect = text_objects("Paused", largeText)
    TextRect.center = ((SCREEN_WIDTH/2), (SCREEN_HEIGHT/2))
    WIN.blit(TextSurf, TextRect)
    
    while True:  # Keep looping until the game is unpaused
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                quit()
            # Additional event handling for unpausing
        pygame.display.update()
        clock.tick(15)
        
def calculate_player_fitness(player: Player) -> int:
    # Weights for each component
    weights = {
        "score": 1,
        "players_eaten": 1, # NOTE: Could have some influence on fitness later on
        "food_eaten": 1, # NOTE: Could have some influence on fitness later on
    }

    # Calculate the score for each component
    score_component = player.score * weights["score"]

    fitness_score = score_component

    if player.failed:
        fitness_score /= 4
    punishment = math.ceil(player.conflicting_moves_counter * CONFLICTING_MOVES_PENALTY)
    if punishment > 0:
        fitness_score -= punishment

    # Return the final fitness score
    return int(fitness_score)


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
        if event_type == pygame.KEYDOWN:
            if event.key == pygame.K_SPACE:
                pause_game()

def pause_game():
    global PAUSED
    PAUSED = not PAUSED

def end_generation(genomes_list, players_list, models_list):
    for i, player in enumerate(players_list):
        genomes_list[i].fitness = calculate_player_fitness(player)
        player.fail_reason = player.fail_reason or "Round time done"
        print(f"{player.name:^10}{genomes_list[i].fitness:^10}", end="")
        fitness_components = get_fitness_components(player)
        for key, value in fitness_components.items():
            value = round(value, 2)
            print(f"{value:^10}", end="")
        print(f"{player.fail_reason:<20}")


def remove_element_from_lists(index, *args):
    if type(index) != int:
        print("Invalid type of index arg")
    for arg in args:
        arg.pop(index)


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


def max_score_reached(players_list):
    MAX_SCORE = max(player.score for player in players_list)
    return MAX_SCORE >= SCORE_LIMIT


def game_finished(players_list):
    round_time_reached = CURRENT_FRAME >= 600
    no_players_left = len(players_list) == 0

    finished =  round_time_reached or \
                max_score_reached(players_list) or no_players_left
    return finished


def ensure_food(food_list, players_list):
    if len(food_list) < NUM_FOOD:
        food_needed = NUM_FOOD - len(food_list)
        food_list.extend(get_food(food_needed, players_list, SCREEN_WIDTH, SCREEN_HEIGHT))


def draw_game(players_list: list[Player], food_list: list[Food], quadtree: QuadTree):
    """Draw the game screen
    Arguments:
        players {list} -- A list of players
        food_list {list} -- A list of food items
    """
    # Background
    WIN.fill((0, 0, 0))
    quadtree.draw(WIN)
    # Get highest score
    MAX_SCORE = max(player.score for player in players_list)

    for player in players_list:
        # Set colour between red and green based on score (0, max_score)
        # 0 = red, max_score = green
        # 0 = 255, max_score = 0
        colour = (255, 0, 0)
        if MAX_SCORE > 0:
            colour = (
                255 - int(player.score / MAX_SCORE * 255),
                int(player.score / MAX_SCORE * 255),
                0,
            )
        player.colour = colour
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
        player_x = selected_player.position.x
        player_y = selected_player.position.y
        food_distances = calculate_and_sort_player_distances(selected_player, food_list)
        nearest_food = list(food_distances.items())[:FOOD_DETECTION]
        for food_name, _ in nearest_food:
            food_obj = next((obj for obj in food_list if obj.name == food_name), None)
            if food_obj:
                pygame.draw.aaline(
                    WIN,
                    (0, 255, 0, 100),
                    (player_x, player_y),
                    (food_obj.position.x, food_obj.position.y),
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
                    (other_player.position.x, other_player.position.y),
                    2,
                )
        # Draw stats for the selected player
        draw_stats(selected_player, WIN, SCREEN_WIDTH)
    
    # # Draw num of collisions
    font = pygame.font.SysFont("Arial", 18)
    text = font.render(f"Collisions: {COLLISIONS}", True, (255, 255, 255))
    WIN.blit(text, (SCREEN_WIDTH *0.9, 10))
    # Draw fps
    fps = font.render(f"FPS: {int(CLOCK.get_fps())}", True, (255, 255, 255))
    WIN.blit(fps, (SCREEN_WIDTH *0.9, 40))
    # Draw calculations
    calculations_text = font.render(f"Calculations: {CALCULATIONS}", True, (255, 255, 255))
    WIN.blit(calculations_text, (SCREEN_WIDTH *0.9, 70))
    pygame.display.flip()


def evaluate_genomes(genomes, config):
    """Evaluate the fitness of each genome in the genomes list
    Arguments:
        genomes {list} -- A list of genomes
        config {neat.config} -- The NEAT configuration file
    """
    global CLOCK, CURRENT_FPS, COLLISIONS, CALCULATIONS, CURRENT_FRAME, SCREEN_WIDTH, SCREEN_HEIGHT, GENERATION, GAME_TIME, WIN  # use the global variable gen and SCREEN
    print(f"{'Name':^10}{'Fitness':^10}{'Peak':^10}{'Score':^10}{'p_eaten':^10}{'f_eaten':^10}{'Distance':^10}{'Death Reason':<20}")

    GENERATION += 1  # update the generation

    # Calculate game's end time from now
    CLOCK = pygame.time.Clock()  # Create a clock object
    start_time = (
        pygame.time.get_ticks()
    )  # reset the start_time after every time we update our generation

    # ! Get the neat components
    neat_components = get_neat_components(genomes, config, SCREEN_WIDTH, SCREEN_HEIGHT)
    players_list = neat_components["players"]
    genomes_list = neat_components["genomes"]
    models_list = neat_components["models"]

    food_list = get_food(NUM_FOOD, players_list, SCREEN_WIDTH, SCREEN_HEIGHT)
    quadtree_area = Rectangle(Vector2(0, 0), Vector2(SCREEN_WIDTH, SCREEN_HEIGHT))
    game_running = True
    CURRENT_FRAME = 0

    # ! GAME LOOP
    while game_running:
        if PAUSED:
            print("Game paused")
            continue
        deleted = 0
        CURRENT_FRAME += 1
        GAME_TIME = round((pygame.time.get_ticks() - start_time) / 1000, 2)  # record the game time for this generation
        CLOCK.tick(FPS)
        COLLISIONS = 0
        CALCULATIONS = 0
        check_for_game_events(players_list)

        # ! Check if the game is finished
        if game_finished(players_list):
            end_generation(genomes_list, players_list, models_list)
            game_running = False
            continue

        quadtree = QuadTree(quadtree_area, 4)
        for particle in players_list + food_list:
            quadtree.insert(particle)

        # Check for collisions
        for player_index in reversed(range(len(players_list))):
            player = players_list[player_index]
            player.colliding = False
            if player.failed:
                delete_player(player_index, players_list, genomes_list, models_list)
                deleted += 1
                continue
            
            # ! Calculate the area around the player
            player.area = Rectangle(Vector2(player.position.x - player.radius, player.position.y - player.radius), 
                                    Vector2(player.radius * 2, player.radius * 2))
            # Check for collisions with other game elements
            others = quadtree.query(player.area)

            for other in others:
                if player != other:
                    CALCULATIONS += 1
                    if player.collides_with(other):
                        COLLISIONS += 1
                        player.colliding = True
                        player.highlight()
                        if other.name.startswith("Player"):
                            # intersecting_player_name = other.name
                            # ! Gets the player object from the players list that has the same name
                            # colliding_player = [this_player for this_player in players_list if this_player.name == intersecting_player_name][0]
                            eaten_colliding_player = player_eaten_player(player, other)
                        elif other.name.startswith("Food"):
                            food = next((obj for obj in food_list if obj.name == other.name), None)
                            player.add_to_score(food.value)
                            player.food_eaten += 1
                            player.last_eaten_time = time.time()
                            # get index of food in food_list
                            food_index = food_list.index(food)
                            remove_element_from_lists(food_index, food_list)
                            quadtree.remove(food)
            # ! Player punishments
            player.score -= int(player.score * SCORE_REDUCTION)

            # ! Gather inputs for player's genome
            inputs = get_inputs(player, players_list, food_list)

            # ! Get the output from the neural network
            output = models_list[player_index].activate(inputs)

            player.process_player_movement(output, SCREEN_WIDTH, SCREEN_HEIGHT)
            
            if player.failed:
                delete_player(player_index, players_list, genomes_list, models_list)
                quadtree.remove(player)
        # ! Ensure there are always correct number of food items on the screen
        ensure_food(food_list, players_list)
        draw_game(players_list, food_list, quadtree)
        quadtree.draw(WIN)
        
        
def main(config_file):
    
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
    neat_pop.run(evaluate_genomes, MAX_GEN)
    
    # Get the most fit genome genome as our winner with the statistics.best_genome() function
    winner = stats.best_genome()
    with open("winner.pkl", "wb") as f:
        pickle.dump(winner, f)
        f.close()
    # Show the final statistics
    print(f'\nBest genome:\n{winner}')


if __name__ == "__main__":
    try:
        print('\033c')
        config_file = 'config-feedforward.txt'

        main(config_file)

    except KeyboardInterrupt:
        print('\nUser quit the game!')
        quit()
