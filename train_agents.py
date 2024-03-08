import os
import pickle
import time

import pygame

import settings
from src import *
from src.assets import Player, Rectangle
from src.neat import *
from src.quadtree import QuadTree
from src.utilities import WindowInformationPacket, check_collision, player_eaten_player
from visualize import *

pygame.init()

infoObject = pygame.display.Info()

SCREEN_WIDTH = infoObject.current_w 
SCREEN_HEIGHT = infoObject.current_h 

WIN = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))

# Game settings
HIGH_SCORE = 0
FPS_LIMIT = settings.game["fps"]
SCORE_LIMIT = settings.game["max_score"]
NUM_FOOD_NEEDED = settings.game["num_food"]

# NEAT settings
GENERATION = 0
MAX_GEN = settings.neat["max_gen"]
FOOD_DETECTION = settings.player["food_detection"]
PLAYER_DETECTION = settings.player["player_detection"]
SCORE_REDUCTION = settings.player["score_reduction"]
PAUSED = False

# Can only eat other players if this player is at least this much bigger
EAT_PLAYER_THRESHOLD = settings.player["eat_player_threshold"]
CONFLICTING_MOVES_PENALTY = 0.0015
SHOWQUADTREE = False
# Initialize the font module
pygame.font.init()

# Render the scores as text
font = pygame.font.SysFont(None, 30)  # Adjust the size as needed


def calculate_player_fitness(player: Player) -> int:
    # TODO: Count number of changes in direction player makes 
    # player.score *= player.punish_score
    return (int(player.score) * int(player.movement_changes)) * int(player.players_eaten)


def end_generation(genomes_list, players_list, models_list):
    for i, player in enumerate(players_list):
        genomes_list[player.id].fitness = calculate_player_fitness(player)
        print(player.id)
        # TODO: Add logging here for each player's fitness


def game_finished(players_list) -> bool:
    MAX_SCORE = max(player.score for player in players_list)
    max_score_reached = MAX_SCORE >= SCORE_LIMIT

    round_time_reached = CURRENT_FRAME >= settings.game["frame_limit"]
    no_players_left = len(players_list) == 0

    finished =  round_time_reached or \
                max_score_reached or \
                no_players_left
    return finished


def ensure_food(food_list, players_list):
    if len(food_list) < NUM_FOOD_NEEDED:
        food_needed = NUM_FOOD_NEEDED - len(food_list)
        food_list.extend(get_food(food_needed, players_list, SCREEN_WIDTH, SCREEN_HEIGHT))


def process_player_collisions(players_list, player):
    for other_player in players_list:
        if player != other_player and check_collision(player, other_player):
            player_eaten_player(player, other_player)


def evaluate_genomes(genomes, config):
    """Evaluate the fitness of each genome in the genomes list
    Arguments:
        genomes {list} -- A list of genomes
        config {modules.neat.config} -- The NEAT configuration file
    """
    global SHOWQUADTREE, CLOCK, CURRENT_FPS, \
        CURRENT_FRAME, SCREEN_WIDTH, SCREEN_HEIGHT, \
        GENERATION, GAME_TIME, WIN, HIGH_SCORE, PAUSED
    print(f"{'Name':^10}{'Fitness':^10}{'Peak':^10}{'Score':^10}{'p_eaten':^10}{'f_eaten':^10}{'Distance':^10}{'Death Reason':<20}")
    SHOWQUADTREE = False
    GENERATION += 1
    CURRENT_FRAME = 0
    WIN = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
    # Calculate game's end time from now
    CLOCK = pygame.time.Clock()  # Create a clock object
    start_time = pygame.time.get_ticks()

    # ! Get the neat components
    neat_components = get_neat_components(genomes, config, SCREEN_WIDTH, SCREEN_HEIGHT)
    players_list = neat_components["players"]
    genomes_list = neat_components["genomes"]
    models_list = neat_components["models"]

    food_list = get_food(NUM_FOOD_NEEDED, players_list, SCREEN_WIDTH, SCREEN_HEIGHT)
    quadtree_area = Rectangle(Vector2(0, 0), Vector2(SCREEN_WIDTH, SCREEN_HEIGHT))
    game_running = True
    
    drawer = Drawer(WIN)
    # ! GAME LOOP
    while game_running:
        check_for_game_events(players_list)
        if PAUSED:
            continue
        
        GAME_TIME = round((pygame.time.get_ticks() - start_time) / 1000, 2)

        info_packet = WindowInformationPacket(
            SCREEN_WIDTH,
            SCREEN_HEIGHT,
            GENERATION,
            round(CLOCK.get_fps()),
            GAME_TIME,
            HIGH_SCORE
        )

        CURRENT_FRAME += 1
        CLOCK.tick(FPS_LIMIT)

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

        selected_player_nearby_players = None
        selected_player_nearby_food = None

        # Check for collisions
        for player_index in reversed(range(len(players_list))):

            player = players_list[player_index]
            player.colliding = False
            if player.failed:
                quadtree.remove(player)
                continue
            
            # ! Calculate the area around the player
            nearby_players = quadtree.query(player.vision_boundary)

            process_player_collisions(nearby_players, player)

            nearby_food = quadtree.query(player.vision_boundary, "Food")
            # TODO: Add ability to draw line from player to closest three players

            for f in nearby_food:
                # TODO: Add ability to draw line from player to closest three food
                if check_collision(f, player):
                    player.add_score(f.value)
                    player.food_eaten += 1
                    food_list.remove(f)
                    quadtree.remove(f)

            # ! Player punishments
            player.punish()

            # ! Gather inputs for player's genome
            inputs = get_inputs(player, nearby_players, nearby_food)

            # ! Get the output from the neural network
            output = models_list[player_index].activate(inputs)
            
            # Normalise the two values in output to be between 0 and 1
            player.move(output, SCREEN_WIDTH, SCREEN_HEIGHT)
            if player.selected:
                selected_player_nearby_players = nearby_players[:3]
                selected_player_nearby_food = nearby_food[:3]
            
        # ! Ensure there are always correct number of food items on the screen
        ensure_food(food_list, players_list)
        if not SHOWQUADTREE:
            quadtree = None
        drawer.draw_game(info_packet, players_list, food_list, quadtree, selected_player_nearby_players, selected_player_nearby_food)
        
        
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
        if (generation +  1) %  1 ==  0:
            date_time = time.strftime("%y_%m_%d_%H_%M")
            filename = "media\\avg_fitness.svg"
            plot_stats(stats, ylog=False, view=False, filename=filename)
            winner = stats.best_genome()
            filename = f"winners\winner_gen_{generation+1}_{date_time}.pkl"
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
