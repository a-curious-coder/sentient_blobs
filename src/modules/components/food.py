import random

import pygame

import settings as settings
from components.particle import Particle
from utilities.general import get_random_colour


class Food(Particle):
    radius = 2

    def __init__(self, position, id):
        super().__init__(id, position, self.radius)
        self.name = f"Food_{id}"
        self.value = settings.food["value"]
        self.highlighted = False
        self.highlightColor = None

    
    def highlight(self, colour = (255, 192, 203)):
        self.highlighted = True
        self.highlightColor = colour

    def draw(self, window):
        """
        Draw the particle on the given window.

        Parameters:
        - window: The pygame window to draw the particle on.

        Returns:
        - None
        """
        r, g, b = self.colour
        if self.highlighted:
            r, g, b = self.highlightColor
        pygame.draw.circle(window, (r, g, b, 100), (self.position.x, self.position.y), self.radius, 1)
        self.highlighted = False

    # def collides_with(self, other):
    #     dx = self.x - other.x
    #     dy = self.y - other.y
    #     distance = math.sqrt(dx * dx + dy * dy)

    #     threshold = self.radius + (self.radius * 0.1) + other.radius

    #     return distance <= threshold