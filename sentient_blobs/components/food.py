import random

import pygame
import settings
from ai_utilities import get_random_colour
from components.game_circle import Circle


class Food(Circle):
    radius = 2

    def __init__(self, x, y, name):
        super().__init__(x, y, self.radius, (255, 0, 255), settings.food["value"])
        self.name = name

    def collides_with(self, other):
        dx = self.x - other.x
        dy = self.y - other.y
        distance = math.sqrt(dx * dx + dy * dy)
        threshold = self.radius + (self.radius * 0.1) + other.radius
        return distance <= threshold