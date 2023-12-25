import pygame
import random
import time

# Player settings

class Player:

    def __init__(self, x, y, name):
        self.x = x
        self.y = y
        self.base_radius = 5
        self.radius = self.base_radius
        self.speed = 3
        self.name = name
        self.color = (random.randint(0, 255), random.randint(0, 255), random.randint(0, 255))
        self.score = 0
        self.players_eaten = 0
        self.player_eaten_time = time.time()
        self.last_move_time = time.time()
        self.wall_touch_time = time.time()
        self.failed = False
        self.distance_travelled = 0
        self.food_consumed = 0
        self.score_rock_bottom = False
        self.fail_reason = ""

    def draw(self, win):
        # Draw the circle itself
        pygame.draw.circle(win, self.color, (self.x, self.y), self.radius)

    def move(self, keys, width, height):
        self.distance_travelled += self.speed

        # Check if the player is touching the left wall
        if keys[pygame.K_LEFT]:
            self.x = max(self.x - self.speed, self.radius)
        elif self.x <= self.radius:
            self.wall_touch_time = time.time()

        # Check if the player is touching the right wall
        if keys[pygame.K_RIGHT]:
            self.x = min(self.x + self.speed, width - self.radius)
        elif self.x >= width - self.radius:
            self.wall_touch_time = time.time()

        # Check if the player is touching the top wall
        if keys[pygame.K_UP]:
            self.y = max(self.y - self.speed, self.radius)
        elif self.y <= self.radius:
            self.wall_touch_time = time.time()

        # Check if the player is touching the bottom wall
        if keys[pygame.K_DOWN]:
            self.y = min(self.y + self.speed, height - self.radius)
        elif self.y >= height - self.radius:
            self.wall_touch_time = time.time()


    
