""" This file contains the Particle class. This class is used to create the circles that are used in the game. """
import pygame
from pygame.math import Vector2


class Particle:
    def __init__(self, id: int, position: Vector2, radius: int, colour: tuple = (128, 128, 128)):
        """
        Initialize a Particle object.

        Parameters:
        - id (int): The id of the particle.
        - x (int): The x-coordinate of the particle's position.
        - y (int): The y-coordinate of the particle's position.
        - radius (int): The radius of the particle.
        - colour (tuple): The colour of the particle in RGB format.

        Returns:
        - None
        """
        self.id = id
        self.position = position
        self.radius = radius
        self.colour = colour

    def get_position(self) -> tuple:
        """
        Get the current position of the particle.

        Parameters:
        - None

        Returns:
        - tuple: The x and y coordinates of the particle's position.
        """
        return self.position.x, self.position.y

    def set_position(self, new_x: int, new_y: int):
        """
        Set the position of the particle.

        Parameters:
        - new_x (int): The new x-coordinate of the particle's position.
        - new_y (int): The new y-coordinate of the particle's position.

        Returns:
        - None
        """
        self.position.x = new_x
        self.position.y = new_y
    
    def set_colour(self, colour: tuple):
        """
        Set the colour of the particle.

        Parameters:
        - colour (tuple): The new colour of the particle in RGB format.

        Returns:
        - None
        """
        self.colour = colour

    def get_quadtree_data(self) -> tuple:
        """
        Get the data of the particle for quadtree representation.

        Parameters:
        - None

        Returns:
        - tuple: x-coordinate, y-coordinate, and radius of the particle.
        """
        return (self.position.x, self.position.y, self.radius)

    def __str__(self) -> str:
        """
        Return a string representation of the particle.

        Parameters:
        - None

        Returns:
        - str: The string representation of the particle.
        """
        return f"{self.id}"

    def __eq__(self, rhs_particle) -> bool:
        """
        Return a bool representing whether the two particles are equal

        Parameters:
        - particle rhs_particle -> particle on right hand side of ==

        Returns:
        - bool: bool representing if the two particles are equal
        """
        is_equal = True
        is_equal &= (self.id == rhs_particle.id)
        is_equal &= (self.position == rhs_particle.position)
        is_equal &= (self.radius == rhs_particle.radius)
        is_equal &= (self.colour == rhs_particle.colour)
        return is_equal
