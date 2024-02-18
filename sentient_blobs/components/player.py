import math
import random
import time

import numpy as np
import pygame
from pygame.math import Vector2

import sentient_blobs.settings as settings
from sentient_blobs.components.particle import Particle
from sentient_blobs.utilities.ai import adjust_output_with_noise
from sentient_blobs.utilities.boundary_shape import Rectangle
from sentient_blobs.utilities.general import (
    conflicting_moves,
    get_distance,
    get_random_colour,
)

pygame.init()
class Player(Particle):
    
    font = pygame.font.SysFont(None, 15)
    
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
        self.speed = settings.player["base_speed"]
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
        self.colliding = False
        self.visited = 0
        self.show_name = False
        self.highlighted = False
        self.highlightColor = None
        
        # New
        vision_distance = 200
        self.vision_boundary = Rectangle(Vector2(position.x - vision_distance // 2, position.y - vision_distance // 2), Vector2(vision_distance, vision_distance))

    def draw(self, screen):
        _radius = self.radius
        # Create surface to draw the player
        surface = pygame.Surface((_radius*2, _radius*2), pygame.SRCALPHA, 32)

        ir, ig, ib = self.colour
        pygame.draw.circle(surface, (ir, ig, ib, 80), (int(_radius), int(_radius)), _radius)

        if self.highlighted:
            r, g, b = self.highlightColor
            pygame.draw.circle(surface, (r, g, b, 255), (int(_radius), int(_radius)), _radius, 2)
        else:
            pygame.draw.circle(surface, (ir, ig, ib, 255), (int(_radius), int(_radius)), _radius, 2)

        self.vision_boundary.draw(surface)
        screen.blit(surface, ( int(self.position.x) - _radius, int(self.position.y) - _radius))
        # pygame.draw.circle(screen, self.color, self.position, self.radius)
        self.highlighted = False
        # Draw id
        if self.show_name:
            text = self.font.render(str(self.id), 1, (255, 255, 255))
            screen.blit(text, (self.position.x - text.get_width() / 2, self.position.y - text.get_height() / 2))

    def move(self, keys, width, height):
        self.distance_travelled += self.speed

        if keys[pygame.K_LEFT]:
            self.position.x = max(self.position.x - self.speed, self.radius)

        if keys[pygame.K_RIGHT]:
            self.position.x = min(self.position.x + self.speed, width - self.radius)

        if keys[pygame.K_UP]:
            self.position.y = max(self.position.y - self.speed, self.radius)

        if keys[pygame.K_DOWN]:
            self.position.y = min(self.position.y + self.speed, height - self.radius)

    def move_randomly(self, screen):
        """ Moves the player randomly at speed within the bounds of the screen """
        keys = {
            pygame.K_LEFT: random.choice([True, False]),
            pygame.K_RIGHT: random.choice([True, False]),
            pygame.K_UP: random.choice([True, False]),
            pygame.K_DOWN: random.choice([True, False]),
        }
        self.move(keys, screen.get_width(), screen.get_height())

    def collides_with(self, other: Particle) -> bool:
        x1, y1, r1 = self.position.x, self.position.y, self.radius
        x2, y2, r2 = other.position.x, other.position.y, other.radius
         # Calculate the distance between the centers of the two circles using the distance formula.
        distance = math.hypot(x1 - x2, y1 - y2)
        threshold = r1 + r2
        # If the distance is less than the sum of the two radii, the circles are colliding.
        return distance <= threshold
        
    def process_player_movement(self, output, w, h):
        keys = {
            pygame.K_LEFT: False,
            pygame.K_RIGHT: False,
            pygame.K_UP: False,
            pygame.K_DOWN: False,
        }

        key_mapping = {
            0: {pygame.K_LEFT},
            1: {pygame.K_RIGHT},
            2: {pygame.K_UP},
            3: {pygame.K_DOWN},
        }
        # Convert the output to probabilities of which choice it's making
        probabilities = np.exp(output) / np.sum(np.exp(output))
        probabilities = adjust_output_with_noise(probabilities)
        # Choose the action with the highest probability
        # NOTE: A single action could select multiple moves as some values represent pairs of simultaneous moves
        max_probability = np.max(probabilities)
        max_indices = np.where(probabilities == max_probability)[0]
        actions = max_indices.tolist()
        ai_chosen_moves = []
        for action in actions:
            # Map the action to corresponding key press(es)
            ai_chosen_moves += key_mapping[action]

        # Map the action to key press(es)
        for key in keys:
            keys[key] = key in ai_chosen_moves

        # ! If any moves are True, check for conflicting moves
        if any(keys):
            self.last_move_time = time.time()
            self.move(keys, w, h)
            self.in_motion = True
        else:
            self.in_motion = False
        
        vision_distance = 200          
        self.vision_boundary = Rectangle(Vector2(self.position.x - vision_distance // 2, self.position.y - vision_distance // 2), Vector2(vision_distance, vision_distance))

    def add_to_score(self, value):
        self.score += value if value >= 1 else 1
        self.radius = self.base_radius + (self.score)
        self.peak_score = max(self.score, self.peak_score)

    def highlight(self, colour=(255, 255, 0)):
        self.highlighted = True
        self.highlightColor = colour

    def punish(self):
        self.score -= (self.score * settings.player['score_reduction']) if self.score > 1 else 0

    def __eq__(self, other):
        return self.name == other.name