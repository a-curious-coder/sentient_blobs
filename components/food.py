import random

import pygame

from utilities import get_random_colour


class Food:
    radius = 2

    def __init__(self, x, y, name):
        self.x = x
        self.y = y
        self.name = name
        self.colour = (random.randint(0, 255), random.randint(0, 255), random.randint(0, 255))
        self.value = 1

    def set_position(self, x, y):
        self.x = x
        self.y = y

    def draw(self, win):
        pygame.draw.circle(win, self.colour, (self.x, self.y), self.radius)
