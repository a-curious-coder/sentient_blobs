""" This file contains the Circle class. This class is used to create the circles that are used in the game. """
import pygame


class Circle:
    def __init__(self, x, y, radius, colour, value):
        self.x = x
        self.y = y
        self.radius = radius
        self.colour = colour
        self.value = value

    def draw(self, win):
        pygame.draw.circle(win, self.colour, (self.x, self.y), self.radius)

    def get_position(self):
        return self.x, self.y

    def set_position(self, x, y):
        self.x = x
        self.y = y
    
    def set_colour(self, colour):
        self.colour = colour
