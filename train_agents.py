import asyncio
import math
import os
import pickle
import random
import sys
import time
from math import floor, sqrt

import numpy as np
import pygame

# Import clock
from pygame import time as pytime

import settings
from src import *
from src.assets import Food, Player, Rectangle
from src.neat import *
from src.quadtree import QuadTree
from src.utilities import check_collision, player_eaten_player

pygame.init()
PAUSED = False
infoObject = pygame.display.Info()
w = infoObject.current_w
h = infoObject.current_h
SCREEN_WIDTH = (w // 3) * 2
SCREEN_HEIGHT = (h // 3) * 2
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
SHOWQUADTREE = False
# Initialize the font module
pygame.font.init()

# Render the scores as text
font = pygame.font.SysFont(None, 30)  # Adjust the size as needed


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
    return int(player.score)


def check_for_game_events(players):
    """Check for game events such as quitting or clicking on a player
    Arguments:
        players {list} -- A list of players

    Returns:
        list -- A list of players
    """
    event_actions = {
        pygame.MOUSEBUTTONDOWN: handle_mousebuttondown
    }

    for event in pygame.event.get():
        event_type = event.type
        if event_type in event_actions:
            event_actions[event_type](event, players)
        if event_type == pygame.KEYDOWN:
            if event.key == pygame.K_SPACE:
                pause_game()
            if event.key == pygame.K_ESCAPE:
                quit_game()
            if event.key == pygame.K_f:
                global SHOWQUADTREE
                SHOWQUADTREE = not SHOWQUADTREE


def end_generation(genomes_list, players_list, models_list):
    for i, player in enumerate(players_list):
        genomes_list[player.id].fitness = calculate_player_fitness(player)
        # TODO: Add logging here for each player's fitness

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


def draw_game(players_list, food_list, quadtree):
    """Draw the game screen
    Arguments:
        players {list} -- A list of players
        food_list {list} -- A list of food items
    """
    # Background
    if SHOWQUADTREE:
        quadtree.draw(WIN)
    # Get highest score
    MAX_SCORE = max(player.score for player in players_list)

    for player in players_list:
        if player.failed:
            continue
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

    fps = font.render(f"FPS: {int(CLOCK.get_fps())}", True, (255, 255, 255))
    score_text = font.render(
        f"Highest Score: {MAX_SCORE:.0f}", True, (255, 255, 255)
    )  # White text
    num_players_text = font.render(
        f"Players Remaining: {len(players_list)}", True, (255, 255, 255)
    )  # White text
    minutes, seconds = divmod(GAME_TIME, 60)
    timer_text = font.render(
        f"Time: {int(minutes)}:{int(seconds):02d}", True, (255, 255, 255)
    )
    generation_text = font.render(f"Generation: {GENERATION}", True, (255, 255, 255))

    WIN.blit(timer_text, (10, 10))  # Position as needed
    WIN.blit(fps, (10, 40))  # Position as needed
    WIN.blit(score_text, (10, 70))  # Position as needed
    WIN.blit(num_players_text, (10, 100))  # Position as needed
    WIN.blit(generation_text, (10, 130))  # Position as needed


    # Find the selected player
    selected_player = next((player for player in players_list if player.selected), None)

    if selected_player:
        selected_player.vision_boundary.draw(WIN)
        # Draw stats for the selected player
        drawer.draw_stats(selected_player, WIN, SCREEN_WIDTH)

    pygame.display.flip()


def process_player_collision(players_list, player):
    colliding_players = [
                    other_player
                    for other_player in players_list
                    if player != other_player and check_collision(player, other_player)
                ]
    for colliding_player in colliding_players:
        player_eaten_player(player, colliding_player)


def evaluate_genomes(genomes, config):
    """Evaluate the fitness of each genome in the genomes list
    Arguments:
        genomes {list} -- A list of genomes
        config {modules.neat.config} -- The NEAT configuration file
    """
    global SHOWQUADTREE, CLOCK, CURRENT_FPS, COLLISIONS, CALCULATIONS, CURRENT_FRAME, SCREEN_WIDTH, SCREEN_HEIGHT, GENERATION, GAME_TIME, WIN  # use the global variable gen and SCREEN
    print(f"{'Name':^10}{'Fitness':^10}{'Peak':^10}{'Score':^10}{'p_eaten':^10}{'f_eaten':^10}{'Distance':^10}{'Death Reason':<20}")
    SHOWQUADTREE = False
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
        check_for_game_events(players_list)
        CURRENT_FRAME += 1
        GAME_TIME = round((pygame.time.get_ticks() - start_time) / 1000, 2)  # record the game time for this generation
        CLOCK.tick(FPS)
        COLLISIONS = 0
        CALCULATIONS = 0

        # ! Check if the game is finished
        if game_finished(players_list):
            end_generation(genomes_list, players_list, models_list)
            game_running = False
            continue

        quadtree = QuadTree(quadtree_area, 4)
        for player in players_list:
            if player.failed:
                continue
            quadtree.insert(player)

        for food in food_list:
            quadtree.insert(food)

        WIN.fill((0, 0, 0))
        # Check for collisions
        for player_index in reversed(range(len(players_list))):

            player = players_list[player_index]
            player.colliding = False
            if player.failed:
                quadtree.remove(player)
                continue
            
            # ! Calculate the area around the player
            nearby_players = quadtree.query(player.vision_boundary)

            process_player_collision(nearby_players, player)

            nearby_food = quadtree.query(player.vision_boundary, "Food")
            # TODO: Add ability to draw line from player to closest three players
                
            # for player_obj in nearby_players:
            #     pygame.draw.aaline(
            #         surface=WIN,
            #         color=(255, 0, 0, 100),
            #         start_pos=(player.position.x, player.position.y),
            #         end_pos=(player_obj.position.x, player_obj.position.y)
            #     )

            for f in nearby_food:
                # TODO: Add ability to draw line from player to closest three food
                # pygame.draw.aaline(
                #     surface=WIN,
                #     color=(255, 255, 0, 100),
                #     start_pos=(player.position.x, player.position.y),
                #     end_pos=(f.position.x, f.position.y)
                # )
                if check_collision(f, player):
                    player.add_to_score(f.value)
                    player.food_eaten += 1
                    food_list.remove(f)
                    quadtree.remove(f)

            # ! Player punishments
            player.score -= int(player.score * SCORE_REDUCTION)

            # ! Gather inputs for player's genome
            inputs = get_inputs(player, nearby_players, nearby_food)

            # ! Get the output from the neural network
            output = models_list[player_index].activate(inputs)
            
            # Normalise the two values in output to be between 0 and 1
            player.move(output, SCREEN_WIDTH, SCREEN_HEIGHT)
            
        # ! Ensure there are always correct number of food items on the screen
        ensure_food(food_list, players_list)
        draw_game(players_list, food_list, quadtree)
        
        
def main(config_file):
    
    # The template for the configuration file can be found here:
    #https://github.com/CodeReclaimers/neat-python/blob/master/examples/xor/config-feedforward
    # The description of the options in the configuration file can be found here:
    #https://neat-python.readthedocs.io/en/latest/config_file.html#defaultgenome-section
    
    # Use NEAT algorithm to build a neural network based on the pre-set configurtion
    # Create a modules.neat.config.Config object from the configuration file
    config = Config(
        DefaultGenome, 
        DefaultReproduction,
        DefaultSpeciesSet, 
        DefaultStagnation,
        config_file
    )
    

    # Create a population.Population object using the Config object created above
    neat_pop = population.Population(config)
    
    # Show the summary statistics of the learning progress
    neat_pop.add_reporter(StdOutReporter(True))
    stats = StatisticsReporter()
    neat_pop.add_reporter(stats)
    
    # Define the folder where winners will be saved
    winners_folder = "winners"
    if not os.path.exists(winners_folder):
        os.makedirs(winners_folder)
    
    # Run the NEAT algorithm for  1000 generations
    for generation in range(MAX_GEN):
        neat_pop.run(evaluate_genomes, 1)  # Run for  1 generation

        # If the generation is a multiple of  10, save the winner
        if (generation +  1) %  10 ==  0:
            winner = stats.best_genome()
            date_time = time.strftime("%y_%m_%d_%H_%M")
            filename = f"winner_gen_{generation+1}_{date_time}.pkl"
            filepath = os.path.join(winners_folder, filename)
            with open(filepath, "wb") as f:
                pickle.dump(winner, f)



if __name__ == "__main__":
    try:
        print('\033c')
        config_file = 'config-feedforward.txt'

        main(config_file)

    except KeyboardInterrupt:
        print('\nUser quit the game!')
        quit()