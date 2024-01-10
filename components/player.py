import random
import time

import pygame


class Player:
    def __init__(self, x, y, name):
        self.name = name
        self.x = x
        self.y = y
        self._score = 0
        self.base_radius = 5
        self._value = 0
        self.speed = 3
        self.colour = (
            random.randint(0, 255),
            random.randint(0, 255),
            random.randint(0, 255),
        )

        self.last_eaten_time = time.time()
        self.players_eaten = 0
        self.food_eaten = 0

        self.distance_travelled = 0
        self.failed = False
        self.fail_reason = "" # Used to log the reason for failure
        self.selected = False # Used to highlight the player

        # ! Punishment counters
        # Log highest score
        self.peak_score = 0
        self.conflicting_moves = False
        self.conflicting_moves_counter = 0
        self.last_move_time = time.time()
        self.in_motion = False

        # ! UNUSED
        self.wall_touch_counter = 0

    def draw(self, win):
        self._value = int(self.base_radius + self.score)
        # Draw the circle itself
        pygame.draw.circle(win, self.colour, (self.x, self.y), self._value)

    def move(self, keys, width, height):
        self.distance_travelled += self.speed

        if keys[pygame.K_LEFT]:
            self.x = max(self.x - self.speed, self._value)

        if keys[pygame.K_RIGHT]:
            self.x = min(self.x + self.speed, width - self._value)

        if keys[pygame.K_UP]:
            self.y = max(self.y - self.speed, self._value)

        if keys[pygame.K_DOWN]:
            self.y = min(self.y + self.speed, height - self._value)

    def add_to_score(self, value):
        self.score += value

    @property
    def score(self):
        return round(self._score)

    @score.setter
    def score(self, value):
        if value < 0:
            self._score = 0
        else:
            self._score = value
    
    @property
    def value(self):
        """ The value is comprised of the player's base radius and the score """
        return round(self._value)

    @value.setter
    def value(self, value):
        if value < 0:
            self._value = 0
        else:
            self._value = value

