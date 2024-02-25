""" This file loads the winner.pkl genome that was saved my main.py and runs the game with it. """
import asyncio
import os
import pickle
import sys
import time

import pygame
from pygame.math import Vector2

import settings
from src import *
from src.neat import *
from src.assets import Food, Player, Rectangle
from src.quadtree import QuadTree
from src.utilities import *

pygame.init()

infoObject = pygame.display.Info()
# Boost resolution for retina displays
pygame.display.set_caption("Sentient Blobs")
w = infoObject.current_w
h = infoObject.current_h
QUADTREE = None
SCREEN_WIDTH = 1024  # Increase the width to make the image sharper
SCREEN_HEIGHT = 1024  # Increase the height to make the image sharper
WIN = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
# WIN = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.NOFRAME)
SCORE_LIMIT = 200  # the maximum score of the game before we break the loop


# Game settings
GAME_PADDING = settings.game["padding"]
NUM_FOOD = settings.game["num_food"]
FPS = settings.game["fps"]
MAX_SCORE = settings.game["max_score"]  # The highest score achieved by a player
FRAME_LIMIT = settings.game["frame_limit"]

# Can only eat other players if this player is at least this much bigger
EAT_PLAYER_THRESHOLD = settings.player["eat_player_threshold"]
FOOD_DETECTION = settings.player["food_detection"]
PLAYER_DETECTION = settings.player["player_detection"]
SCORE_REDUCTION = settings.player["score_reduction"]

# Can only eat other players if this player is at least this much bigger
EAT_PLAYER_THRESHOLD =settings.player["eat_player_threshold"]
print("LOADED SETTINGS")
def load_player(winner_genome_path):
    # Load the config file, which is assumed to live in
    # the same directory as this script.
    config_path = "config-feedforward.txt"
    config = neat.Config(neat.DefaultGenome, neat.DefaultReproduction,
                    neat.DefaultSpeciesSet, neat.DefaultStagnation,
                    config_path)

    # Load the winner genome.
    if not os.path.exists(winner_genome_path):
        print("Error: winner.pkl file not found. Please train a winner model first.")
        # Add any additional error handling or instructions here
    else:
        try:
            with open(winner_genome_path, 'rb') as f:
                winner_genome = pickle.load(f)
        except Exception as e:
            print(e)
            print("Error: Unable to load winner.pkl file. Please ensure the file is valid.")
            # Add any additional error handling or instructions here

    # Create the winner net.
    winner_net = nn.create(winner_genome, config)
    return winner_net


def remove_element_from_lists(index, *args):
    if type(index) != int:
        print("Invalid type of index arg")
    for arg in args:
        arg.pop(index)


def delete_player(player_index, players_list, models_list):
    player = players_list[player_index]

    # ! Print out the stats of the player to console
    fitness_components = get_fitness_components(player)
    print(f"{player.name:^10}", end="")
    for key, value in fitness_components.items():
        value = round(value, 2)
        print(f"{value:^10}", end="")
    print(f"{player.fail_reason:<20}")

    # ! Remove player, genome and model from the lists as we've modified the genome by reference (fucking hope I have)
    remove_element_from_lists(player_index, players_list, models_list)


def max_score_reached(players_list):
    MAX_SCORE = max(player.score for player in players_list)
    return MAX_SCORE >= SCORE_LIMIT


def game_finished(players_list):
    round_time_reached = CURRENT_FRAME >= FRAME_LIMIT
    no_players_left = len(players_list) == 0

    finished =  round_time_reached or \
                max_score_reached(players_list) or \
                no_players_left
    return finished


def check_for_game_events(players, models):
    """Check for game events such as quitting or clicking on a player
    Arguments:
        players {list} -- A list of players

    Returns:
        list -- A list of players
    """
    event_actions = {
        pygame.QUIT: quit_game,
        pygame.KEYDOWN: handle_keydown,
        pygame.MOUSEBUTTONDOWN: handle_mousebuttondown,
    }

    for event in pygame.event.get():
        # print(event)
        event_type = event.type
        if event_type in event_actions:
            event_actions[event_type](event, players)
        elif event.type == pygame.DROPFILE:
            print("File dropped")
            filepath = event.file
            _, ext = os.path.splitext(filepath)
            if ext == ".pkl":
                # Load the .pkl file into your neural network
                new_player_path = filepath
                with open(new_player_path, 'rb') as f:
                    new_genome = pickle.load(f)
                config = neat.Config(neat.DefaultGenome, neat.DefaultReproduction,
                                neat.DefaultSpeciesSet, neat.DefaultStagnation,
                                "config-feedforward.txt")
                net = neat.nn.FeedForwardNetwork.create(new_genome, config)
                # Calculate mouse position
                mouse_x, mouse_y = pygame.mouse.get_pos()
                players.append(Player(Vector2(mouse_x, mouse_y), len(players)+1))
                models.append(net)

                print(f"Loaded player model from {filepath}")
            else:
                print(f"Invalid file type. Only .pkl files are accepted.")
        # If player clicks on button, let them upload a .pkl file to play with
        

    return players


def process_player_collision(players_list, player):
    colliding_players = [
                    other_player
                    for other_player in players_list
                    if player != other_player and check_collision(player, other_player)
                ]
    for colliding_player in colliding_players:
        player_eaten_player(player, colliding_player)


def ensure_food(food_list, players_list):
    if len(food_list) < NUM_FOOD:
        food_needed = NUM_FOOD - len(food_list)
        food_list.extend(get_food(food_needed, players_list, SCREEN_WIDTH, SCREEN_HEIGHT))


async def draw_game(players_list, food_list):
    """Draw the game screen
    Arguments:
        players {list} -- A list of players
        food_list {list} -- A list of food items
    """
    # Background
    WIN.fill((0, 50, 0))

    # Get highest score
    MAX_SCORE = max(player.score for player in players_list)

    for player in players_list:
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
    minutes, seconds = divmod(GAME_TIME, 60)
    timer_text = font.render(
        f"Time: {int(minutes)}:{int(seconds):02d}", True, (255, 255, 255)
    )
    WIN.blit(timer_text, (10, 100))  # Position as needed
    # Draw the scores onto the screen
    WIN.blit(score_text, (10, 10))  # Position as needed
    WIN.blit(num_players_text, (10, 40))  # Position as needed

    # Find the selected player
    selected_player = next((player for player in players_list if player.selected), None)

    if selected_player:
        nearest_food_obj = QUADTREE.query(selected_player.vision_boundary, object_type="Food")
        nearest_player_obj = QUADTREE.query(selected_player.vision_boundary, "Player")
        selected_player.vision_boundary.draw(WIN)

        for food_obj in nearest_food_obj:
            pygame.draw.aaline(
                surface=WIN,
                color=(255, 255, 0, 100),
                start_pos=(selected_player.position.x, selected_player.position.y),
                end_pos=(food_obj.position.x, food_obj.position.y)
            )

        for player_obj in nearest_player_obj:
            pygame.draw.aaline(
                surface=WIN,
                color=(255, 0, 0, 100),
                start_pos=(selected_player.position.x, selected_player.position.y),
                end_pos=(player_obj.position.x, player_obj.position.y)
            )

        # Draw stats for the selected player
        draw_stats(selected_player, WIN, SCREEN_WIDTH)
    # Draw box for dropping AI pkl files
    pygame.draw.rect(WIN, (255, 255, 255), (10, SCREEN_HEIGHT - 60, 200, 50))
    drop_text = font.render("Drop AI pkl file here", True, (0, 0, 0))
    WIN.blit(drop_text, (20, SCREEN_HEIGHT - 50))
    pygame.display.flip()
    await asyncio.sleep(0)


async def main():
    """ Game loop """
    print(f"Screen resolution: {w}x{h}")
    global QUADTREE
    global CURRENT_FRAME, SCREEN_WIDTH, SCREEN_HEIGHT, GAME_TIME, FRAME_LIMIT, SCORE_LIMIT, WIN  # use the global variable gen and SCREEN
    region = Rectangle(Vector2(0, 0), Vector2(SCREEN_WIDTH, SCREEN_HEIGHT))
    while True:
        print(f"{'Name':^10}{'Fitness':^10}{'Peak':^10}{'Score':^10}{'p_eaten':^10}{'f_eaten':^10}{'Distance':^10}{'Death Reason':<20}")


        # Load all pkl files with winner_ prefix
        winners = []
        winner_path = os.getcwd() + "//winners"
        if not os.path.exists(winner_path):
            print("No winner files found in location {}".format(winner_path))
            break
        # Get all the files in the current directory
        files = os.listdir(winner_path)
        winner_genome_path = None
        if len(files) == 0:
            print("No winner files found")
            break
        for file in files:
            if file.startswith("winner_") and file.endswith(".pkl"):
                winner_genome_path = file
                print(winner_path + "//" + winner_genome_path)
                winners.append(load_player(winner_path + "//" + winner_genome_path))

        # ! Load the winner
        # Calculate game's end time from now
        clock = pygame.time.Clock()  # Create a clock object
        start_time = (pygame.time.get_ticks())

        players_list = []
        models_list = []

        for winner in winners:
            random_x = random.randint(GAME_BORDER, SCREEN_WIDTH - GAME_BORDER)
            random_y = random.randint(GAME_BORDER, SCREEN_HEIGHT - GAME_BORDER)
            players_list.append(Player(Vector2(random_x, random_y), len(players_list)+1))
            models_list.append(winner)
        food_list = get_food(NUM_FOOD, players_list, SCREEN_WIDTH, SCREEN_HEIGHT)

        game_running = True
        CURRENT_FRAME = 0

        # ! GAME LOOP
        while game_running:
            CURRENT_FRAME += 1
            QUADTREE = QuadTree(region, 4)
            # ! Check if the game is finished
            if game_finished(players_list):
                players_list.pop()
                models_list.pop()
                game_running = False
                continue

            players_list = check_for_game_events(players_list, models_list)

            # ! Reset the quadtree
            for player in players_list:
                QUADTREE.insert(player)
            
            for food in food_list:
                QUADTREE.insert(food)

            GAME_TIME = round((pygame.time.get_ticks() - start_time) / 1000, 2)  # record the game time for this generation

            clock.tick(FPS)

            # Update player positions and check for collisions
            for player_index in reversed(range(len(players_list))):
                
                player = players_list[player_index]

                if player.failed:
                    delete_player(player_index, players_list, models_list)
                    continue

                nearby_players = QUADTREE.query(player.vision_boundary)
                player.vision_boundary.draw(WIN)
                process_player_collision(nearby_players, player)

                nearby_food = QUADTREE.query(player.vision_boundary, "Food")
                for f in nearby_food:
                    if check_collision(f, player):
                        player.add_to_score(f.value)
                        player.food_eaten += 1
                        player.last_eaten_time = time.time()
                        food_list.remove(f)
                        QUADTREE.remove(f)

                # ! Player punishments
                starve_value = int(player.score * SCORE_REDUCTION)
                
                player.score -= starve_value

                # ! Gather inputs for player's genome
                inputs = get_inputs(player, nearby_players, nearby_food)

                # ! Get the output from the neural network
                output = models_list[player_index].activate(inputs)

                player.process_player_movement(output, SCREEN_WIDTH, SCREEN_HEIGHT)
                
                if player.failed:
                    delete_player(player_index, players_list, models_list)
                
                player.peak_score = max(player.score, player.peak_score)

            # ! Ensure there are always correct number of food items on the screen
            ensure_food(food_list, players_list)
            
            await draw_game(players_list, food_list)
            await asyncio.sleep(0)


asyncio.run(main())
