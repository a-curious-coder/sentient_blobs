""" This file loads the winner.pkl genome that was saved my main.py and runs the game with it. """
import asyncio
import os
import pickle
import time

import settings
from collision_logic import check_collision, player_eaten_player
from components.food import Food
from components.player import Player
from drawer import draw_stats
from game_event_handler import (
    activity_detected,
    handle_keydown,
    handle_mousebuttondown,
    quit_game,
)
from getters import *
from neat import *

pygame.init()

infoObject = pygame.display.Info()
# Boost resolution for retina displays
pygame.display.set_caption("Sentient Blobs")
w = infoObject.current_w
h = infoObject.current_h

SCREEN_WIDTH = 1920  # Increase the width to make the image sharper
SCREEN_HEIGHT = 1080  # Increase the height to make the image sharper
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
def load_player():
    # Load the config file, which is assumed to live in
    # the same directory as this script.
    config_path = "config-feedforward.txt"
    config = neat.Config(neat.DefaultGenome, neat.DefaultReproduction,
                    neat.DefaultSpeciesSet, neat.DefaultStagnation,
                    config_path)

    # Load the winner genome.
    winner_genome_path = "winner.pkl"
    with open(winner_genome_path, 'rb') as f:
        winner_genome = pickle.load(f)

    # Create the winner net.
    winner_net = neat.nn.FeedForwardNetwork.create(winner_genome, config)
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
                players.append(
                    Player(
                        mouse_x,
                        mouse_y,
                        f"Player {len(players)+1}",
                    )
                )
                models.append(net)

                print(f"Loaded player model from {filepath}")
            else:
                print(f"Invalid file type. Only .pkl files are accepted.")

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
        # Draw lines to the 10 nearest foods to the selected player
        player_x = selected_player.x
        player_y = selected_player.y
        food_distances = calculate_and_sort_player_distances(selected_player, food_list)
        nearest_food = list(food_distances.items())[:FOOD_DETECTION]
        for food_name, _ in nearest_food:
            food_obj = next((obj for obj in food_list if obj.name == food_name), None)
            if food_obj:
                pygame.draw.aaline(
                    surface=WIN,
                    colour=(0, 255, 0, 100),
                    start_pos=(player_x, player_y),
                    end_pos=(food_obj.x, food_obj.y)
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
                    surface=WIN,
                    colour=(255, 0, 0, 100),
                    start_pos=(player_x, player_y),
                    end_pos=(other_player.x, other_player.y),
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

    while True:
        global CURRENT_FRAME, SCREEN_WIDTH, SCREEN_HEIGHT, GAME_TIME, FRAME_LIMIT, SCORE_LIMIT, WIN  # use the global variable gen and SCREEN

        print(f"{'Name':^10}{'Fitness':^10}{'Peak':^10}{'Score':^10}{'p_eaten':^10}{'f_eaten':^10}{'Distance':^10}{'Death Reason':<20}")

        # ! Load the winner
        winner_net = load_player()

        # Calculate game's end time from now
        clock = pygame.time.Clock()  # Create a clock object
        start_time = (pygame.time.get_ticks())


        random_x = SCREEN_WIDTH // 2
        random_y = SCREEN_HEIGHT // 2
        print(f"Player 1: {random_x}, {random_y}")
        players_list = []

        players_list.append(
            Player(
                random_x,
                random_y,
                f"Player {len(players_list)+1}",
            )
        )

        models_list = [winner_net]

        for _ in range(50):
            random_x = random.randint(GAME_BORDER, SCREEN_WIDTH - GAME_BORDER)
            random_y = random.randint(GAME_BORDER, SCREEN_HEIGHT - GAME_BORDER)
            players_list.append(
                Player(
                    random_x,
                    random_y,
                    f"Player {len(players_list)+1}",
                )
            )
            models_list.append(winner_net)
        food_list = get_food(NUM_FOOD, players_list, SCREEN_WIDTH, SCREEN_HEIGHT)

        game_running = True
        CURRENT_FRAME = 0

        # ! GAME LOOP
        while game_running:
            CURRENT_FRAME += 1

            # ! Check if the game is finished
            if game_finished(players_list):
                players_list.pop()
                models_list.pop()
                game_running = False
                continue

            players_list = check_for_game_events(players_list, models_list)

            GAME_TIME = round((pygame.time.get_ticks() - start_time) / 1000, 2)  # record the game time for this generation

            clock.tick(FPS)

            # Update player positions and check for collisions
            for player_index in reversed(range(len(players_list))):
                
                player = players_list[player_index]

                if player.failed:
                    delete_player(player_index, players_list, models_list)
                    continue

                process_player_collision(players_list , player)

                # ! Player punishments
                starve_value = int(player.score * SCORE_REDUCTION)
                
                player.score -= starve_value

                # ! Gather inputs for player's genome
                inputs = get_inputs(player, players_list, food_list)

                # ! Get the output from the neural network
                output = models_list[player_index].activate(inputs)

                player.process_player_movement(output, SCREEN_WIDTH, SCREEN_HEIGHT)
                
                if player.failed:
                    delete_player(player_index, players_list, models_list)
                
                player.peak_score = max(player.score, player.peak_score)


            # ! Update food positions and check for collisions
            for food_item in food_list[:]:
                for player in players_list:
                    if check_collision(food_item, player):
                        # player.add_to_score(food_item.value)
                        player.score += 1
                        player.food_eaten += 1
                        player.last_eaten_time = time.time()
                        food_list.remove(food_item)
                        break

            # ! Ensure there are always correct number of food items on the screen
            ensure_food(food_list, players_list)
            
            await draw_game(players_list, food_list)
            await asyncio.sleep(0)


if __name__ == "__main__":
    asyncio.run(main())
