import math
import random
import time

import numpy as np
import pygame
from pygame.math import Vector2

import settings as settings

from ..utilities.ai import adjust_output_with_noise
from ..utilities.general import conflicting_moves, get_distance, get_random_colour
from .boundary_shape import Rectangle
from .particle import Particle

pygame.init()
class Player(Particle):
    
    font = pygame.font.SysFont(None, 15)
    vision_distance = 200
    
    def __init__(self, position, id):
        """
        Initialize a Player object.

        Parameters:
        - position (Position): The location of the player     
        - id (int): The id of the player (used to identify the player in the game)
        
        Returns:
        - None
        """
        super().__init__(id, position, settings.player["base_radius"])
        self.name = f"Player_{id}"
        self.score = 0
        self.base_radius = settings.player["base_radius"]
        self.speed = settings.player["max_speed"]
        self.players_eaten = 0
        self.food_eaten = 0

        self.distance_travelled = 0
        self.failed = False
        self.fail_reason = "" # Used to log the reason for failure
        self.selected = False # Used to highlight the player
        self.angle_input = 0
        # ! Punishment counters
        # Log highest score
        self.peak_score = 0
        self.colliding = False
        self.show_name = False
        self.highlighted = False
        self.highlightColor = None
        self.movement_angle = 0
        self.angle_in_degrees = 0
        # New
        self.vision_boundary = Rectangle(Vector2(position.x - (self.vision_distance // 2) - self.radius, 
                                                position.y - (self.vision_distance // 2) - self.radius), 
                                        Vector2(self.vision_distance, 
                                                self.vision_distance))
        self.nn_outputs = None
        self.movement_changes = 0
        self.no_change_count = 0
        self.punish_score = 1

    def draw(self, screen):
        _radius = self.radius
        # Calculate the width and height of the rectangle based on vision_distance
        width = self.vision_distance + (2 * _radius)
        height = self.vision_distance + (2 * _radius)

        # Calculate the top-left corner of the rectangle
        top_left = Vector2(self.position.x - (self.vision_distance //  2) - _radius,  
                        self.position.y - (self.vision_distance //  2) - _radius)
        # Create the Rectangle object using the top-left corner and the width and height
        self.vision_boundary = Rectangle(Vector2(top_left.x, top_left.y), Vector2(width, height))
        # Create surface to draw the player
        surface = pygame.Surface((_radius*3, _radius*3), pygame.SRCALPHA, 32)

        ir, ig, ib = self.colour
        pygame.draw.circle(surface, (128, 128, 128, 80), (int(_radius), int(_radius)), _radius)

        if self.highlighted:
            r, g, b = self.highlightColor
            pygame.draw.circle(surface, (r, g, b, 255), (int(_radius), int(_radius)), _radius, 2)
        else:
            pygame.draw.circle(surface, (ir, ig, ib, 255), (int(_radius), int(_radius)), _radius, 2)

        # self.vision_boundary.draw(screen)

        screen.blit(surface, (int(self.position.x) - _radius, int(self.position.y) - _radius))
        # pygame.draw.circle(screen, self.color, self.position, self.radius)
        self.highlighted = False
        # Draw id
        if self.show_name:
            text = self.font.render(str(self.id), 1, (255, 255, 255))
            screen.blit(text, (self.position.x - text.get_width() / 2, self.position.y - text.get_height() / 2))
        
    def move(self, output, width, height):
        # Ensure output has at least two elements
        if len(output) < 2:
            raise ValueError("Output must contain at least two elements for angle and speed.")

        # Ensure self.speed is a positive number
        if self.speed < 0:
            raise ValueError("Player speed must be a positive number.")
        min_speed = 0
        self.nn_outputs = output
        if self.angle_input != self.nn_outputs[0]:
            self.movement_changes += 1
        else:
            self.no_change_count += 1
        if self.no_change_count > 150:
            self.punish_score *= 0.9
        self.angle_input = output[0]
        # Convert the output between 0 and 1 to an angle in radians
        angle_in_radians = (output[0] + 1) * math.pi

        # Convert angle to value between 0 and 360
        self.movement_angle = int(math.degrees(angle_in_radians) % 360)

        self.set_max_speed()

        # Convert the second of two outputs to a speed between 0 and 1
        # self.speed = max(settings.player["min_speed"], output[1] * self.speed)
        self.speed = round(min_speed + (output[1] + 1) * (settings.player["max_speed"] - min_speed) / 2, 2)
        # Calculate the new position using anglee
        new_x = self.position.x  + math.cos(angle_in_radians) * self.speed
        new_y = self.position.y + math.sin(angle_in_radians) * self.speed
        
        # Wrap around the boundaries of the map
        if new_x < 0:
            new_x = width
        elif new_x > width:
            new_x = 0

        if new_y < 0:
            new_y = height
        elif new_y > height:
            new_y = 0

        self.position.x = new_x
        self.position.y = new_y
    
    def move_toward_food(self, food, width, height):
        # Calculate the difference in x and y coordinates
        dx = food.position.x - self.position.x
        dy = food.position.y - self.position.y
        

        # Calculate the angle in radians and convert to degrees
        angle_in_radians = math.atan2(dy, dx)
        angle_degrees = math.degrees(angle_in_radians)

        # Calculate the new position using anglee
        new_x = self.position.x  + math.cos(angle_in_radians) * self.speed
        new_y = self.position.y + math.sin(angle_in_radians) * self.speed
        self.speed = round(2 * (settings.player["max_speed"]) / 2, 2)

        # Wrap around the boundaries of the map
        if new_x < 0:
            new_x = width
        elif new_x > width:
            new_x = 0

        if new_y < 0:
            new_y = height
        elif new_y > height:
            new_y = 0

        self.position.x = new_x
        self.position.y = new_y

    def add_score(self, value):
        self.score += value if value >= 1 else 1
        if value < 1:
            self.score += 1
        
        if self.score >= 60:
            self.radius = self.base_radius + 60 + (self.score - 60) * 0.5
        elif self.score >= 90:
            self.radius = self.base_radius + 90 + (self.score - 90) * 0.25
        else:
            self.radius = self.base_radius + (self.score)
        self.peak_score = max(self.score, self.peak_score)

    def highlight(self, colour=(255, 255, 0)):
        self.highlighted = True
        self.highlightColor = colour

    def punish(self):
        self.score -= (self.score * settings.player['score_reduction']) if self.score > 1 else 0

    def set_max_speed(self):
        # Ensure speed is a value between min_speed and max_speed based on the player's score
        speed = (1 - (self.score / settings.player["speed_reduction_rate"])) * settings.player["max_speed"]
        self.speed = max(speed, settings.player["min_speed"])

    def set_colour(self, max_score = 1):
        max_score = 1 if max_score <= 0 else max_score
        self.colour = (
                    255 - int(self.score / max_score * 255),
                    int(self.score / max_score * 255),
                    0,
                )

    def __eq__(self, other):
        return self.name == other.name