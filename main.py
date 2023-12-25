import math
import pygame
import random
import neat
import numpy as np
import time
from math import sqrt
import logging
import sys
from components.food import Food
from components.player import Player

# Create a custom logger
logger = logging.getLogger(__name__)

# Set the level of the logger. This can be DEBUG, INFO, WARNING, ERROR, CRITICAL.
logger.setLevel(logging.ERROR)

# Create a console handler
ch = logging.StreamHandler()

# Create a formatter
formatter = logging.Formatter('[%(levelname)s]\t%(message)s')

# Add the formatter to the console handler
ch.setFormatter(formatter)

# Add the console handler to the logger
logger.addHandler(ch)

pygame.init()

SCREEN_WIDTH = 800
SCREEN_HEIGHT = 800
GAME_BORDER = 50
WIN = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))

FPS = 30 # Desired frames per second
SCORE_LIMIT = 100 #the maximum score of the game before we break the loop


# Game settings
NUM_FOOD = 100
ROUND_TIME = 30

# NEAT settings
GENERATION = 0 

# Global settings
THRESHOLD_INACTIVITY = 3
PUNISHMENT_EATEN = 2
PUNISHMENT_INACTIVITY = 5

# Checks if user wants to exit / play manually
def check_for_game_events():
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            quit()
        # Person presses escape
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                pygame.quit()
                quit()

# An AI has played well enough to win
def goal_reached(players_list):
    global max_score
    max_score = max(player.score for player in players_list)
    return max_score >= SCORE_LIMIT

def calculate_fitness(player):
    # Weights for each component
    weights = {'score': 1.2, 'players_eaten': 1, 'food_consumed': 0.5, 
                'position': 0.1, 'speed': 0.1, 'agility': 0.1, 'strategy': 0.1, 
                'players_consumed': 0.2, 'distance_travelled': 0.2}

    # Calculate the score for each component
    score_component = player.score * weights['score']
    # print(f"Score component: {score_component}")
    players_eaten_component = player.players_eaten * weights['players_eaten']
    # print(f"Players eaten component: {players_eaten_component}")
    food_consumed_component = player.food_consumed * weights['food_consumed']
    # print(f"Food consumed component: {food_consumed_component}")
    distance_travelled_component = player.distance_travelled * weights['distance_travelled']
    # print(f"Distance travelled component: {distance_travelled_component}")

    fitness_score = score_component \
    + players_eaten_component \
    + food_consumed_component \
    + distance_travelled_component

    # print(f"Intermediate fitness score: {fitness_score}")

    if player.failed:
        fitness_score /= 2
    fitness_score = int(fitness_score)

    # Return the final fitness score
    return fitness_score

def evaluate_genomes(genomes, config):
    global SCREEN_WIDTH, SCREEN_HEIGHT, GENERATION, game_time, WIN, manual_control #use the global variable gen and SCREEN
    print(f"{'Fitness':^10}{'Reason':<50}")
    GENERATION += 1 #update the generation
    
    # Calculate game's end time from now
    end_round_time = ROUND_TIME + time.time()
    clock = pygame.time.Clock() # Create a clock object
    start_time = pygame.time.get_ticks() #reset the start_time after every time we update our generation

    
    # ! Get the neat components
    neat_components = get_neat_components(genomes, config)
    
    players_list = neat_components['players']
    genomes_list = neat_components['genomes']
    models_list = neat_components['models']
    food_list = get_food(NUM_FOOD)


    while True:
        
        if time.time() >= end_round_time:
            for player_index, player in enumerate(players_list):
                genomes_list[player_index].fitness = calculate_fitness(player)
            print("Round time done")
            for i in reversed(range(3)):
                print(f"Starting next generation in {i+1}...", end='\r')
            break

        # Continue the game loop
        check_for_game_events()

        if len(players_list) == 0:
            run = False
            break

        if goal_reached(players_list):
            run = False
            break

        game_time = round((pygame.time.get_ticks() - start_time)/1000, 2) #record the game time for this generation

        clock.tick(FPS)
        
        keys = {
            pygame.K_LEFT: False, 
            pygame.K_RIGHT: False, 
            pygame.K_UP: False, 
            pygame.K_DOWN: False
        }

        key_mapping = {
            0: {pygame.K_LEFT},
            1: {pygame.K_RIGHT},
            2: {pygame.K_UP},
            3: {pygame.K_DOWN},
            4: {pygame.K_LEFT, pygame.K_RIGHT},
            5: {pygame.K_UP, pygame.K_RIGHT},
            6: {pygame.K_UP, pygame.K_LEFT},
            7: {pygame.K_UP, pygame.K_DOWN}
        }

        delete_player = False
        player_text = f"{'Moved':^10}{'Name':^10}"
        
        # Update player positions and check for collisions
        for player_index in reversed(range(len(players_list))):
            
            delete_player = False
            player = players_list[player_index]

            # Collect neural network input data
            player_distances = list(get_nearest_players_distances(player, players_list).values())
            player_sizes = list(get_nearest_players_sizes(player, players_list).values())
            food_distances = list(get_nearest_players_distances(player, food_list).values())
            wall_distances = get_distance_to_walls(player)

            # Convert the collected data to a format the neural network will recognise
            # ! Player location
            # ! Player score
            # ! Player radius
            # ! Player distances to other players
            # ! Player sizes of other players
            # ! Player distances to food
            # ! Player distances to walls
            inputs = tuple([player.x, player.y, player.score, player.radius] + player_distances + player_sizes + food_distances + wall_distances)

            # Get neural network output
            output = models_list[player_index].activate(inputs)

            # Convert the output to probabilities of which choice it's making
            probabilities = np.exp(output) / np.sum(np.exp(output))

            # Choose the action with the highest probability
            # NOTE: A single action could select multiple moves as some values represent pairs of simultaneous moves
            action = np.argmax(probabilities)

            # Map the action to corresponding key press(es)
            ai_chosen_moves = key_mapping[action]

            # Map the action to key press(es)
            for key in keys:
                keys[key] = key in ai_chosen_moves
            
            if any(keys.values()):
                # TODO: Better define later
                conflicting_moves = (keys[pygame.K_LEFT] and keys[pygame.K_RIGHT]) or \
                                    (keys[pygame.K_DOWN] and keys[pygame.K_UP])

            if not conflicting_moves:
                player.last_move_time = time.time()
                # Move player
                current_x, current_y = player.x, player.y
                player.move(keys, SCREEN_WIDTH, SCREEN_HEIGHT)
                new_x, new_y = player.x, player.y
                # Has player movesf
                player_moved = current_x != new_x or current_y != new_y
                # if player_moved:
                    # player_text += f"{'Yes':^10}{player.name:^10}\n"
            # else:
                # player_text += f"{'No':^10}{player.name:^10}\n"

            # reset keys for next player
            for key in keys:
                keys[key] = False

            def calculate_time_diff(current_time, last_time) -> float:
                return current_time - last_time

            def apply_penalty(player, current_time, last_time, reason) -> list:
                INACTIVITY_TIME = THRESHOLD_INACTIVITY
                if reason == "Hasn't eaten anything":
                    INACTIVITY_TIME = 15
                delete_player = False
                inactivity_time = calculate_time_diff(current_time, last_time)
                if inactivity_time > INACTIVITY_TIME:
                    if player.score_rock_bottom == True:
                        delete_player = True
                        player.fail_reason = reason
                        return [delete_player, last_time]
                    player.score = max(0, player.score - THRESHOLD_INACTIVITY)
                    last_time = current_time
                    if player.score == 0:
                        player.score_rock_bottom = True
                        last_time = current_time
                return [delete_player, last_time]

            current_time = time.time()
            result = apply_penalty(player, current_time, player.last_move_time, "Hasn't moved")
            delete_player, player.last_move_time = result[0], result[1]
            if not delete_player:
                result = apply_penalty(player, current_time, player.player_eaten_time, "Hasn't eaten anything")
                delete_player, player.player_eaten_time = result[0], result[1]

            if not delete_player:
                result = apply_penalty(player, current_time, player.wall_touch_time, "Touching wall")
                delete_player, player.wall_touch_time = result[0], result[1]


            if not delete_player:
                # Store players colliding with this player
                colliding_players = [other_player for other_player in players_list if player != other_player and check_collision(player, other_player)]
                for colliding_player in colliding_players:
                    if handle_collision(player, colliding_player):
                        delete_player = True
                        player.fail_reason = f"{player.name} eaten by {colliding_player.name}"
                        break
                
            if delete_player:
                # Set the fitness score
                genomes_list[player_index].fitness = calculate_fitness(player)
                print(f"{genomes_list[player_index].fitness:^10}{player.fail_reason:<50}")
                # Remove them from the lists as we've modified the genome by reference (fucking hope I have)
                players_list.pop(player_index)
                models_list.pop(player_index)
                genomes_list.pop(player_index)

        # if player_text != "":
        #     sys.stdout.write(player_text + '\r')
        #     sys.stdout.flush()
        # Update food positions and check for collisions
        for food_item in food_list[:]: # Use a copy of the list to avoid issues with removing items during iteration
            for player in players_list:
                if check_collision(food_item, player):
                    player.score += 1
                    player.food_consumed += 1
                    player.player_eaten_time = time.time()
                    food_list.remove(food_item)
                    break

        # Ensure there are always correct number of food items on the screen
        if len(food_list) < NUM_FOOD:
            food_needed = NUM_FOOD - len(food_list)
            food_list.extend(get_food(food_needed))

        draw_game(players_list, food_list, game_time)

# ! DRAW
def draw_game(players, food, game_time):
    # Background
    WIN.fill((0, 0, 0))

    game_objects = players + food

    for obj in game_objects:
        obj.draw(WIN)

    # Initialize the font module
    pygame.font.init()

    # Render the scores as text
    font = pygame.font.SysFont(None, 30) # Adjust the size as needed
    score_text = font.render(f"Highest Score: {max_score}", True, (255, 255, 255)) # White text
    num_players_text = font.render(f"Players Remaining: {len(players)}", True, (255, 255, 255)) # White text
    generation_text = font.render(f"Generation: {GENERATION}", True, (255, 255, 255))
    minutes, seconds = divmod(game_time, 60)
    timer_text = font.render(f"Time: {int(minutes)}:{int(seconds):02d}", True, (255, 255, 255))
    WIN.blit(timer_text, (10, 100)) # Position as needed
    # Draw the scores onto the screen
    WIN.blit(score_text, (10, 10)) # Position as needed
    WIN.blit(num_players_text, (10, 40)) # Position as needed
    WIN.blit(generation_text, (10, 70))

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
    distance = math.sqrt(dx*dx + dy*dy)
    return distance <= (obj1.radius + obj2.radius)

def handle_collision(player, colliding_player):
    if player.score > colliding_player.score:
        player.score += colliding_player.score // 2
        player.players_eaten += 1
        player.player_eaten_time = time.time()
        colliding_player.failed = True
        colliding_player.fail_reason += f"{player.name} has eaten {colliding_player.name}"
        return False
    colliding_player.score += player.score // 2
    colliding_player.players_eaten += 1
    colliding_player.player_eaten_time = time.time()
    player.failed = True

    return True

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

def get_nearest_players_distances(player, players):
    distances = {}
    for other_player in players:
        if other_player != player:
            dx = other_player.x - player.x
            dy = other_player.y - player.y
            distance = sqrt(dx*dx + dy*dy)
            distance -= 2 * min(player.radius, other_player.radius) # Subtract twice the radius
            distances[other_player.name] = distance

    # Sort the dictionary by values (distances)
    sorted_distances = dict(sorted(distances.items(), key=lambda item: item[1]))

    # If there aren't 10 players, fill the remaining slots with 9999
    while len(sorted_distances) < 10:
        sorted_distances[f"Player_{len(sorted_distances)+1}"] = 9999

    # Get the nearest 10 players
    return dict(sorted(sorted_distances.items(), key=lambda item: item[1])[:10])

def get_nearest_players_sizes(player, players):
    # Assuming get_nearest_players_distances function is available
    nearest_players = get_nearest_players_distances(player, players)

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
                random.randint(
                    GAME_BORDER, 
                    SCREEN_WIDTH - GAME_BORDER
                ), 
                random.randint(
                    GAME_BORDER, 
                    SCREEN_HEIGHT - GAME_BORDER
                ), 
                f'Player {len(players_list)+1}'
            )
        )
        # Initialize the fitness score to 0
        genome.fitness = 0
        genomes_list.append(genome)
        # Create a neural network for each genome
        model = neat.nn.FeedForwardNetwork.create(genome, config)  # Set up the neural network for each genome using the configuration we set
        models_list.append(model)  # Append the neural network in the list
    
    # Return a dictionary of lists
    return {
        'players': players_list,
        'genomes': genomes_list,
        'models': models_list
    }

def get_food(n: int) -> list:
    ''' Returns a list of 100 food items
    These are plotted within the game screen
    
    Returns:
        list -- A list of n food items
    '''
    return [
                Food(
                    random.randint(GAME_BORDER, SCREEN_WIDTH - GAME_BORDER), 
                    random.randint(GAME_BORDER, SCREEN_HEIGHT - GAME_BORDER), 
                    f'Food {number}'
                ) 
                for number in range(n)
            ]