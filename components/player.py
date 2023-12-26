import pygame
import random
import time


class Player:

    def __init__(self, x, y, name, colour=(255, 255, 255)):
        self.x = x
        self.y = y
        self.base_radius = 5
        self.radius = self.base_radius
        self.speed = 3
        self.name = name
        self.color = colour
        self._score = 0
        self.players_eaten = 0
        self.last_eaten_time = time.time()
        self.last_move_time = time.time()
        self.wall_touch_time = time.time()
        self.failed = False
        self.distance_travelled = 0
        self.food_consumed = 0
        self.score_rock_bottom = False
        self.fail_reason = ""
        self.edge_touch_counter = 0
        self.selected = False
        # ! Punishment counters
        # TODO: Start incrementing punishment counters
        self.eaten_punishment_counter = 0
        self.move_punishment_counter = 0
        self.wall_punishment_counter = 0
        # Log highest score
        self.peak_score = 0

    def draw(self, win):
        self.radius = int(self.base_radius + self.score)
        # Draw the circle itself
        pygame.draw.circle(win, self.color, (self.x, self.y), self.radius)

    def move(self, keys, width, height):
        self.distance_travelled += self.speed

        if keys[pygame.K_LEFT]:
            self.x = max(self.x - self.speed, self.radius)

        if keys[pygame.K_RIGHT]:
            self.x = min(self.x + self.speed, width - self.radius)

        if keys[pygame.K_UP]:
            self.y = max(self.y - self.speed, self.radius)

        if keys[pygame.K_DOWN]:
            self.y = min(self.y + self.speed, height - self.radius)

    @property
    def score(self):
        return self._score
    
    @score.setter
    def score(self, value):
        if value < 0:
            self._score = 0
        else:
            self._score = value
