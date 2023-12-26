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
ROUND_TIME = 15

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

# Checks if user wants to exit / play manually
def check_for_game_events(players):
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            quit()
        # Person presses escape
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                pygame.quit()
                quit()
        elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:  # Left mouse button clicked
            mouse_x, mouse_y = pygame.mouse.get_pos()
            # Check if the mouse click is within the bounding box of any player
            for player in players:
                if (player.x - player.radius <= mouse_x <= player.x + player.radius and
                        player.y - player.radius <= mouse_y <= player.y + player.radius):
                    # Invert the selected boolean
                    player.selected = not player.selected
                else:
                    player.selected = False
    return players

# An AI has played well enough to win
def goal_reached(players_list):
    global max_score
    max_score = max(player.score for player in players_list)
    return max_score >= SCORE_LIMIT

def get_fitness_components(player):
    weights = {
                'peak_score': 1,
                'score': 1, 
                'players_eaten': 1,
                'food_consumed': 1, 
                'distance_travelled': 1}
    
    return {
        'peak_score': player.peak_score * weights['peak_score'],
        'score': player.score * weights['score'],
        'players_eaten': player.players_eaten * weights['players_eaten'],
        'food_consumed': player.food_consumed * weights['food_consumed'],
        'distance_travelled': int(player.distance_travelled * weights['distance_travelled'])
    }

def calculate_fitness(player):
    # Weights for each component
    weights = {
                'peak_score': 0.5,
                'score': 1, 
                'players_eaten': 1,
                'food_consumed': 1, 
                'distance_travelled': 0.3}
    
    # peak_score_component = player.peak_score * weights['peak_score']
    # Calculate the score for each component
    score_component = player.score * weights['score']
    # print(f"Score component: {score_component}")
    # players_eaten_component = player.players_eaten * weights['players_eaten']
    # print(f"Players eaten component: {players_eaten_component}")
    # food_consumed_component = player.food_consumed * weights['food_consumed']
    # print(f"Food consumed component: {food_consumed_component}")
    # distance_travelled_component = player.distance_travelled * weights['distance_travelled']
    # print(f"Distance travelled component: {distance_travelled_component}")

    fitness_score = score_component
    # + peak_score_component \
    # + players_eaten_component \
    # + food_consumed_component 

    # Get punishment components
    # fitness_score -= player.eaten_punishment_counter * PUNISHMENT_EATEN
    # fitness_score -= player.move_punishment_counter * PUNISHMENT_INACTIVITY
    # fitness_score -= player.wall_punishment_counter * PUNISHMENT_INACTIVITY
    # print(f"Intermediate fitness score: {fitness_score}")

    if player.failed:
        fitness_score /= 2
        
    fitness_score = int(fitness_score)

    # Return the final fitness score
    return fitness_score

def evaluate_genomes(genomes, config):
    global SCREEN_WIDTH, SCREEN_HEIGHT, GENERATION, game_time, WIN, manual_control #use the global variable gen and SCREEN
    print(f"{'Name':^10}{'Fitness':^10}{'Peak':^10}{'score':^10}{'p_eaten':^10}{'f_eaten':^10}{'distance':^10}{'Reason':<20}")

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
        
        if time.time() >= end_round_time or len(players_list) < 2:
            for player_index, player in enumerate(players_list):
                genomes_list[player_index].fitness = calculate_fitness(player)
            print("Round time done")
            for i in reversed(range(3)):
                print(f"Starting next generation in {i+1}...", end='\r')
                time.sleep(1)
            break

        # Continue the game loop
        players_list = check_for_game_events(players_list)

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
        player_text = []
        
        # Update player positions and check for collisions
        for player_index in reversed(range(len(players_list))):
            # player_text = []
            delete_player = False
            player = players_list[player_index]
            player.score = player.score - (player.score * 0.002) if player.score > 0 else 0
            
            # ! inputs
            # Collect neural network input data
            player_distances = list(get_nearest_players_distances(player, players_list).values())[:PLAYER_DETECTION]
            player_sizes = list(get_nearest_players_sizes(player, players_list).values())[:PLAYER_DETECTION]
            food_distances = list(get_nearest_players_distances(player, food_list).values())[:FOOD_DETECTION]
            wall_distances = get_distance_to_walls(player)

            # Convert the collected data to a format the neural network will recognise
            # ! Player location
            # ! Player score
            # ! Player radius
            # ! Player distances to other players
            # ! Player sizes of other players
            # ! Player distances to food
            # ! Player distances to walls
            inputs = tuple([player.peak_score, player.x, player.y, player.radius] + player_distances + player_sizes + food_distances)

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

            # ! Reset keys for next player
            for key in keys:
                keys[key] = False

            # def calculate_time_diff(current_time, last_time) -> float:
            #     return current_time - last_time

            # current_time = time.time()
            # # ! Check if player has moved
            # delete_player = False
            # player_inactivity_time = calculate_time_diff(current_time, player.last_move_time)
            # if player_inactivity_time > THRESHOLD_INACTIVITY:
            #     # ! If player has hit rock bottom, delete them
            #     if player.score_rock_bottom == True:
            #         delete_player = True
            #         player.fail_reason = f"Hasn't moved"
            #     else:
            #         player.score = max(0, player.score - PUNISHMENT_INACTIVITY)
            #         player.last_move_time = time.time()
            #         player.move_punishment_counter += 1
            #         if player.score == 0:
            #             player.score_rock_bottom = True
            
            # # ! Check if player is touching the wall
            # if not delete_player:
            #     # Is player touching the wall.
            #     # Check if the player is touching the edge
            #     if player.x - player.radius <= 0 or player.x + player.radius >= SCREEN_WIDTH or player.y - player.radius <= 0 or player.y + player.radius >= SCREEN_HEIGHT:
            #         player.edge_touch_counter += 1
            #     else:
            #         player.edge_touch_counter = 0

            #     # If the player has been touching the edge for more than N seconds, trigger an action
            #     if player.edge_touch_counter > FPS * THRESHOLD_INACTIVITY:
            #         # Reset the counter
            #         player.edge_touch_counter = 0
            #         if player.score_rock_bottom == True:
            #             delete_player = True
            #             player.fail_reason = f"Touching wall"
            #             # player_text.append(f"{player.name:^10} - {player.fail_reason:>10}")                       
            #         player.score = max(0, player.score - PUNISHMENT_INACTIVITY)
            #         player.edge_touch_counter = 0
            #         player.wall_punishment_counter += 1
            #         if player.score == 0:
            #             player.score_rock_bottom = True
            #     # result = apply_penalty(player, current_time, player.wall_touch_time, "Touching wall")
            #     # delete_player, player.wall_touch_time = result[0], result[1]
            
            # # ! TODO: Check if player has eaten any food
            # # ! Check if player has eaten another player or food
            # if not delete_player:
            #     INACTIVITY_TIME = 5
            #     # When was the last time the player ate anything
            #     current_time = time.time()
                
            #     inactivity_time = calculate_time_diff(current_time, player.last_eaten_time)
            #     if inactivity_time > INACTIVITY_TIME:
            #         if player.score_rock_bottom == True:
            #             dfelete_player = True
            #             player.fail_reason = "Hasn't eaten anything"
                    
            #         player.score = max(0, player.score - PUNISHMENT_INACTIVITY)
            #         # Reset this time
            #         player.last_eaten_time = time.time()
            #         player.eaten_punishment_counter += 1
            #         if player.score == 0:
            #             player.score_rock_bottom = True

            
            if not delete_player:
                # Store players colliding with this player
                colliding_players = [other_player for other_player in players_list if player != other_player and check_collision(player, other_player)]
                for colliding_player in colliding_players:
                    if player_is_eaten(player, colliding_player):
                        delete_player = True
                        player.fail_reason = f"Eaten by {colliding_player.name}"
                        break
                
            if delete_player:
                # Set the fitness score
                genomes_list[player_index].fitness = calculate_fitness(player)
                fitness_components = get_fitness_components(player)
                # ! PRINT STATS
                
                print(f"{player.name:^10}{genomes_list[player_index].fitness:^10}", end="")
                for key, value in fitness_components.items():
                    print(f"{value:^10}", end="")
                print(f"{player.fail_reason:<20}")
                # Set the player as failed
                players_list[player_index].failed = True
                # Remove them from the lists as we've modified the genome by reference (fucking hope I have)
                players_list.pop(player_index)
                models_list.pop(player_index)
                genomes_list.pop(player_index)

        if player_text != []:
            print(*player_text, sep="\n")

        # ! Update food positions and check for collisions
        for food_item in food_list[:]: # Use a copy of the list to avoid issues with removing items during iteration
            for player in players_list:
                if check_collision(food_item, player):
                    player.score += 1
                    player.peak_score = max(player.score, player.peak_score)
                    player.food_consumed += 1
                    player.last_eaten_time = time.time()
                    food_list.remove(food_item)
                    break

        # Ensure there are always correct number of food items on the screen
        if len(food_list) < NUM_FOOD:
            food_needed = NUM_FOOD - len(food_list)
            food_list.extend(get_food(food_needed))

        
        draw_game(players_list, food_list, game_time)

# ! DRAW
def draw_game(players, food_list, game_time):
    # Background
    WIN.fill((0, 0, 0))

    # Get highest score
    global max_score
    max_score = max(player.score for player in players)
    
    for player in players:
        # Set colour between red and green based on score (0, max_score)
        # 0 = red, max_score = green
        # 0 = 255, max_score = 0
        color = (255, 255, 255)
        if max_score > 0:
            color = (255 - int(player.score / max_score * 255), int(player.score / max_score * 255), 0)
        player.color = color
        player.draw(WIN)

    for food in food_list:
        food.draw(WIN)

    # Initialize the font module
    pygame.font.init()

    # Render the scores as text
    font = pygame.font.SysFont(None, 30) # Adjust the size as needed
    score_text = font.render(f"Highest Score: {max_score:.0f}", True, (255, 255, 255)) # White text
    num_players_text = font.render(f"Players Remaining: {len(players)}", True, (255, 255, 255)) # White text
    generation_text = font.render(f"Generation: {GENERATION}", True, (255, 255, 255))
    minutes, seconds = divmod(game_time, 60)
    timer_text = font.render(f"Time: {int(minutes)}:{int(seconds):02d}", True, (255, 255, 255))
    WIN.blit(timer_text, (10, 100)) # Position as needed
    # Draw the scores onto the screen
    WIN.blit(score_text, (10, 10)) # Position as needed
    WIN.blit(num_players_text, (10, 40)) # Position as needed
    WIN.blit(generation_text, (10, 70))

    # Find the selected player
    selected_player = next((player for player in players if player.selected), None)

    if selected_player:
        # Draw lines to the 10 nearest foods to the selected player
        player_x = selected_player.x
        player_y = selected_player.y
        food_distances = get_nearest_players_distances(selected_player, food_list)
        nearest_food = list(food_distances.items())[:FOOD_DETECTION]
        for food_name, _ in nearest_food:
            food_obj = next((obj for obj in food_list if obj.name == food_name), None)
            if food_obj:
                pygame.draw.aaline(WIN, (0, 255, 0, 100), (player_x, player_y), (food_obj.x, food_obj.y), 2)

        # Draw lines to the 10 nearest players to the selected player
        player_distances = get_nearest_players_distances(selected_player, players)
        nearest_players = list(player_distances.items())[:PLAYER_DETECTION]
        for player_name, _ in nearest_players:
            other_player = next((obj for obj in players if obj.name == player_name), None)
            if other_player:
                pygame.draw.aaline(WIN, (255, 0, 0, 100), (player_x, player_y), (other_player.x, other_player.y), 2)

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
    threshold = obj1.radius + (obj1.radius * 0.1) + obj2.radius
    return distance <= threshold

def player_is_eaten(player, colliding_player):
    # ! this player ate other player
    if player.fail_reason == "" and player.score > colliding_player.score:
        player.score += 5 + colliding_player.score
        player.peak_score = max(player.score, player.peak_score)
        player.players_eaten += 1
        player.last_eaten_time = time.time()
        colliding_player.failed = True
        colliding_player.fail_reason += f"eaten by {player.name}"
        return False
    elif player.score == colliding_player.score:
        return False
    # ! This player has been eaten
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