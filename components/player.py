import random
import time

import pygame

import settings


class Player:
    def __init__(self, x, y, name):
        self.name = name
        self.x = x
        self.y = y
        self.score = 0
        self.radius = 0
        self.base_radius = settings.player["base_radius"]
        self.speed = settings.player["base_speed"]
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

    def draw(self, win):
        # Draw the circle itself
        pygame.draw.circle(win, self.colour, (self.x, self.y), self.radius)

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


    def add_to_score(self, value):
        self.score += value
        self.peak_score = max(self.score, self.peak_score)

    def punish(self):
        self.score -= (self.score * settings.player['score_reduction']) if self.score > 1 else 0


    @property
    def radius(self):
        return self.base_radius + self.score
    
    @radius.setter
    def radius(self, value):
        self.base_radius = max(0, value - self.score)

    @property
    def value(self):
        """ The value is comprised of the player's base radius and the score """
        return round(self.base_radius + self.score)
    
    @value.setter
    def value(self, value):
        if value < 0:
            self.radius = 0
        else:
            self.radius = value