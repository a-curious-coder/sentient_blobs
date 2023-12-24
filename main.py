import math
import pygame
import random
import neat
import numpy as np
import time
from math import sqrt
import logging

from food import Food
from player import Player

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

screen_width = 800
screen_height = 600
WIN = pygame.display.set_mode((screen_width, screen_height))

control_key = pygame.K_SPACE # Change this to any key you want
fps = 30 # Desired frames per second
score_limit = 100 #the maximum score of the game before we break the loop


#NEAT options
generation = 0 
failed_punishment = 2
INACTIVITY_PUNISHMENT = 5

ROUND_TIME = 30
INACTIVITY_THRESHOLD = 3
PUNISHMENT = 5

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
    if collide_with_wall(player, screen_width, screen_height):
        return True
    return False

# Checks if user wants to exit / play manually
def check_for_game_events():
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            run = False
            pygame.quit()
            quit()
            break
        elif event.type == pygame.KEYDOWN:
            if event.key == control_key:
                manual_control = not manual_control

# An AI has played well enough to win
def goal_reached(players_list):
    global max_score
    max_score = max(player.score for player in players_list)
    return max_score >= score_limit


def get_player_fitness(player):
    # Weights for each component
    weights = {'score': 0.7, 'players_eaten': 0.3}

    # Calculate the score for each component
    score_component = player.score * weights['score']
    players_eaten_component = player.players_eaten * weights['players_eaten']

    # Normalize the components
    total_weight = sum(weights.values())
    score_component /= total_weight
    players_eaten_component /= total_weight

    fitness_score = score_component + players_eaten_component

    if player.failed:
        fitness_score /= 2
    # Calculate the final fitness score

    return int(fitness_score)

def get_player_fitness(player):
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
    print(f"{fitness_score:^10}{player.fail_reason:<50}")

    # Return the final fitness score
    return fitness_score



def game_loop(genomes, config):
    global generation, game_time, WIN, manual_control #use the global variable gen and SCREEN
    print(f"{'Fitness':^10}{'Reason':<50}")
    generation += 1 #update the generation
    clock = pygame.time.Clock() # Create a clock object
    start_time = pygame.time.get_ticks() #reset the start_time after every time we update our generation

    food_list = []
    for _ in range(100): # Always start with 100 food items
        food_list.append(Food(random.randint(50, 750), random.randint(50, 550), f'Food {len(food_list)+1}'))
    
    players_list = []
    genomes_list = []
    models_list = []
    for _, genome in genomes: # Replace 10 with the desired number of players
        players_list.append(Player(random.randint(50, 750), random.randint(50, 550), 5, f'Player {len(players_list)+1}'))
        genome.fitness = 0
        genomes_list.append(genome)
        model = neat.nn.FeedForwardNetwork.create(genome, config) #set up the neural network for each genome using the configuration we set
        models_list.append(model) #append the neural network in the list


    run = True
    manual_control = False
    screen_width = 800
    screen_height = 600
    
    end = ROUND_TIME + time.time()
    while run:
        if time.time() >= end:
            run = False
            for player_index, player in players_list:
                genomes_list[player_index].fitness = get_player_fitness(player)
            print("Round time done")
            break
        # Find the highest score and the number of remaining players
        check_for_game_events()

        if len(players_list) == 0:
            run = False
            break


        if goal_reached(players_list):
            run = False
            break

        game_time = round((pygame.time.get_ticks() - start_time)/1000, 2) #record the game time for this generation

        clock.tick(fps)

        
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

        pressed_keys = pygame.key.get_pressed()
        delete_player = False
        player_text = ""
        # Update player positions and check for collisions
        for player_index in reversed(range(len(players_list))):
            player = players_list[player_index]
            delete_player = False

        
            player_distances = list(get_nearest_players_distances(player, players_list).values())
            player_sizes = list(get_nearest_players_sizes(player, players_list).values())
            food_distances = list(get_nearest_players_distances(player, food_list).values())
            wall_distances = get_distance_to_walls(player)

            # Convert the collected data to a format the nearal network will recognise
            inputs = tuple([player.x, player.y, player.score, player.radius] + player_distances + player_sizes + food_distances + wall_distances)

            output = models_list[player_index].activate(inputs)

            # Convert the output to probabilities
            probabilities = np.exp(output) / np.sum(np.exp(output))

            # Choose the action with the highest probability
            action = np.argmax(probabilities)
            # Map the action to a key press
            ai_chosen_moves = key_mapping[action]

            # Map the action to a key press
            for key in keys:
                keys[key] = key in ai_chosen_moves
            current_x, current_y = player.x, player.y
            player.move(keys, screen_width, screen_height)
            new_x, new_y = player.x, player.y
            player_moved = not (current_x == new_x and current_y == new_y)
            if any(keys.values()):
                # TODO: Better define later
                conflicting_moves = not (keys[pygame.K_LEFT] and keys[pygame.K_RIGHT]) and not (keys[pygame.K_DOWN] and keys[pygame.K_UP])
                if player_moved and conflicting_moves:
                    player.last_move_time = time.time()
                    player_text += f"{player.name} is moving\n"
            else:
                player_text += f"{player.name} is not moving\n"
            for key in keys:
                keys[key] = False

            
            current_time = time.time()
            result = current_time - player.last_move_time
            result2 = current_time - player.player_eaten_time
            result3 = current_time - player.wall_touch_time

            # Define penalties
            penalty = player.score // 10

            # Apply penalties if inactivity threshold is exceeded
            if result > INACTIVITY_THRESHOLD:
                # ! Player hasn't moved
                if player.score_rock_bottom == True:
                    delete_player = True
                    player.fail_reason = "Hasn't moved"
                    break
                player.score = max(0, player.score - penalty)
                player.last_move_time = current_time
                if player.score == 0:
                    player.score_rock_bottom = True
                    player.last_move_time = current_time
                    

            if result2 > INACTIVITY_THRESHOLD:
                # ! Player hasn't eaten another player
                if player.score_rock_bottom == True:
                    delete_player = True
                    player.fail_reason = "Hasn't eaten anyone"
                    break
                player.score = max(0, player.score - penalty)
                player.player_eaten_time = current_time
                if player.score == 0:
                    player.score_rock_bottom = True
                    player.last_move_time = current_time
                    

            if result3 > INACTIVITY_THRESHOLD:
                # ! Player hasn't moved away from wall/boundary of game
                if player.score_rock_bottom == True:
                    delete_player = True
                    player.fail_reason = "Touching wall"
                    break
                player.score = max(0, player.score - penalty)
                player.wall_touch_time = current_time
                if player.score == 0:
                    player.score_rock_bottom = True
                    player.last_move_time = current_time
                    




            if not delete_player:
                # Store players colliding with this player
                colliding_players = [other_player for other_player in players_list if player != other_player and check_collision(player, other_player)]
                for colliding_player in colliding_players:
                    if handle_collision(player, colliding_player):
                        delete_player = True
                        player.fail_reason = f"{player.name} eaten by {colliding_player.name}"
                        break
                
            if player.failed == True or delete_player == True:
                genomes_list[player_index].fitness = get_player_fitness(player)
                # if genomes_list[player_index].fitness != 0:
                    # print(f"{player.name}\t{genomes_list[player_index].fitness}")
                players_list.pop(player_index)
                models_list.pop(player_index)
                genomes_list.pop(player_index)
        if player_text != "":
            print(player_text)
        # Update food positions and check for collisions
        for food_item in food_list[:]: # Use a copy of the list to avoid issues with removing items during iteration
            for player in players_list:
                if check_collision(food_item, player):
                    player.score += 1
                    player.food_consumed += 1
                    food_list.remove(food_item)
                    break

        # Ensure there are always 100 food items on the screen
        while len(food_list) < 100:
            food_list.append(
                Food(
                    random.randint(0, screen_width), 
                    random.randint(0, screen_height), 
                    f'Food {len(food_list)+1}'
                )
            )

        draw_game(players_list, food_list, game_time)
    print("done?")


# def get_nearest_players_distances(player, players):
#     distances = []
#     for other_player in players:
#         if other_player != player:
#             dx = other_player.x - player.x
#             dy = other_player.y - player.y
#             distance = sqrt(dx*dx + dy*dy)
#             distance -= 2 * min(player.radius, other_player.radius) # Subtract twice the radius
#             distances.append(distance)
#     distances.sort()

#     # If there aren't 10 players, fill the remaining slots with 9999
#     while len(distances) < 10:
#         distances.append(9999)

#     return distances[:10] # Get the nearest 10 players


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


# def get_nearest_players_sizes(player, players_list):
#     sizes = []
#     for other_player in players_list:
#         if other_player != player:
#             sizes.append(other_player.radius)
#     sizes.sort()

#     # If there aren't 10 players, fill the remaining slots with 9999
#     while len(sizes) < 10:
#         sizes.append(9999)

#     return sizes[:10] # Get the nearest 10 players

# Draw everything onto the screen
def draw_game(players, food, game_time):
    WIN.fill((0, 0, 0))

    for player in players:
        player.draw(WIN)
    for food_item in food:
        food_item.draw(WIN)

    num_remaining_players = len(players)

    # Initialize the font module
    pygame.font.init()

    # Render the scores as text
    font = pygame.font.SysFont(None, 30) # Adjust the size as needed
    score_text = font.render(f"Highest Score: {max_score}", True, (255, 255, 255)) # White text
    num_players_text = font.render(f"Players Remaining: {num_remaining_players}", True, (255, 255, 255)) # White text
    generation_text = font.render(f"Generation: {generation}", True, (255, 255, 255))
    minutes, seconds = divmod(game_time, 60)
    timer_text = font.render(f"Time: {int(minutes)}:{int(seconds):02d}", True, (255, 255, 255))
    WIN.blit(timer_text, (10, 100)) # Position as needed
    # Draw the scores onto the screen
    WIN.blit(score_text, (10, 10)) # Position as needed
    WIN.blit(num_players_text, (10, 40)) # Position as needed
    WIN.blit(generation_text, (10, 70))

    pygame.display.update()


def check_collision(obj1, obj2):
    dx = obj1.x - obj2.x
    dy = obj1.y - obj2.y
    distance = math.sqrt(dx*dx + dy*dy)
    return distance <= (obj1.radius + obj2.radius)


def collide_with_wall(player, screen_width, screen_height):
    if player.x + player.radius >= screen_width or player.x - player.radius <= 0:
        return True
    if player.y + player.radius >= screen_height or player.y - player.radius <= 0:
        return True
    return False


def get_distance_to_walls(player):
    x0 = player.x
    y0 = player.y
    r = player.radius
    L = 0
    R = screen_width
    T = 0
    B = screen_height
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
