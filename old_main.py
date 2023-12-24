import math
import pygame
import random

from food import Food
from player import Player

pygame.init()

screen_width = 800
screen_height = 600
win = pygame.display.set_mode((screen_width, screen_height))

control_key = pygame.K_SPACE # Change this to any key you want
fps = 60 # Desired frames per second
clock = pygame.time.Clock() # Create a clock object
generation = 0

def game_loop(players, food):
    run = True
    manual_control = False
    screen_width = 800
    screen_height = 600
    while run:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False
            elif event.type == pygame.KEYDOWN:
                if event.key == control_key:
                    manual_control = not manual_control
        keys = {pygame.K_LEFT: False, pygame.K_RIGHT: False, pygame.K_UP: False, pygame.K_DOWN: False}
        pressed_keys = pygame.key.get_pressed()

        # Update player positions and check for collisions
        for i, player in enumerate(players):
            if i == 0:
                if manual_control:
                    player.update(pressed_keys, screen_width, screen_height)
                else:
                    random_key = random.choice([pygame.K_LEFT, pygame.K_RIGHT, pygame.K_UP, pygame.K_DOWN])
                    keys[random_key] = True
                    player.update(keys, screen_width, screen_height)
                    keys[random_key] = False
            else:
                random_key = random.choice([pygame.K_LEFT, pygame.K_RIGHT, pygame.K_UP, pygame.K_DOWN])
                keys[random_key] = True
                player.update(keys, screen_width, screen_height)
                keys[random_key] = False
            colliding_players = [other_player for other_player in players if player != other_player and check_collision(player, other_player)]
            for colliding_player in colliding_players:
                if player.score > colliding_player.score:
                    player.score += 1 # Increment the score of the larger player
                    players.remove(colliding_player)
                else:
                    players.remove(player)

        # Update food positions and check for collisions
        for food_item in food[:]: # Use a copy of the list to avoid issues with removing items during iteration
            for player in players:
                if check_collision(food_item, player):
                    player.score += 1
                    food.remove(food_item)
                    break

        # Ensure there are always 100 food items on the screen
        while len(food) < 100:
            food.append(Food(random.randint(0, screen_width), random.randint(0, screen_height)))

        draw_game(players, food);
        # Limit FPS
        clock.tick(fps)

    pygame.quit()


def draw_game(players, food):
    # Draw everything onto the screen
    win.fill((0, 0, 0))
    for player in players:
        player.draw(win)
    for food_item in food:
        food_item.draw(win)

    # Find the highest score and the number of remaining players
    max_score = max(player.score for player in players)
    num_remaining_players = len(players)

    # Initialize the font module
    pygame.font.init()

    # Render the scores as text
    font = pygame.font.SysFont(None, 30) # Adjust the size as needed
    score_text = font.render(f"Highest Score: {max_score}", True, (255, 255, 255)) # White text
    num_players_text = font.render(f"Players Remaining: {num_remaining_players}", True, (255, 255, 255)) # White text
    generation_text = font.render(f"Generation: {generation}")
    # Draw the scores onto the screen
    win.blit(score_text, (10, 10)) # Position as needed
    win.blit(num_players_text, (10, 40)) # Position as needed

    pygame.display.update()



def check_collision(obj1, obj2):
    dx = obj1.x - obj2.x
    dy = obj1.y - obj2.y
    distance = math.sqrt(dx*dx + dy*dy)
    return distance <= (obj1.radius + obj2.radius)


players = []
for _ in range(10): # Replace 10 with the desired number of players
    players.append(Player(random.randint(0, 800), random.randint(0, 600), 10, f'Player {len(players)+1}'))
food = []
for _ in range(100): # Always start with 100 food items
    food.append(Food(random.randint(0, 800), random.randint(0, 600)))


game_loop(players, food);