import pygame
from pygame.locals import *


class QuadTree:
    def __init__(self, boundary: Rect, capacity: int):
        self.boundary = boundary
        self.capacity = capacity
        self.game_objects = []

        self.divided = False
    
    def insert(self, game_object):
        """ Inserts a game object into the quadtree 
        
        Args:
            game_object (tuple): A tuple of (x, y, radius) coordinates and radius.
        
        Returns:
            bool: True if the game object was inserted, False otherwise.
        """
        x, y, radius = game_object.x, game_object.y, game_object.radius
        if not self.boundary.colliderect(pygame.Rect(x - radius, y - radius, radius * 2, radius * 2)):
            return False
        
        if len(self.game_objects) < self.capacity:
            self.game_objects.append(game_object)
            return True
        else:
            if not self.divided:
                self.subdivide()
            
            if self.northwest.insert(game_object):
                return True
            elif self.northeast.insert(game_object):
                return True
            elif self.southwest.insert(game_object):
                return True
            elif self.southeast.insert(game_object):
                return True
    
    def subdivide(self):
        """ Divides the quadtree into four quadtrees """
        x = self.boundary.x
        y = self.boundary.y
        w = self.boundary.width
        h = self.boundary.height

        nw = pygame.Rect(x, y, w / 2, h / 2)
        ne = pygame.Rect(x + w / 2, y, w / 2, h / 2)
        sw = pygame.Rect(x, y + h / 2, w / 2, h / 2)
        se = pygame.Rect(x + w / 2, y + h / 2, w / 2, h / 2)

        self.northwest = QuadTree(nw, self.capacity)
        self.northeast = QuadTree(ne, self.capacity)
        self.southwest = QuadTree(sw, self.capacity)
        self.southeast = QuadTree(se, self.capacity)

        self.divided = True

    def query(self, range):
        found = []
        if not self.boundary.colliderect(range):
            return found
        
        for game_object in self.game_objects:
            x, y, radius = game_object.x, game_object.y, game_object.radius
            if range.colliderect(pygame.Rect(x - radius, y - radius, radius * 2, radius * 2)):
                found.append(game_object)
        
        if self.divided:
            found += self.northwest.query(range)
            found += self.northeast.query(range)
            found += self.southwest.query(range)
            found += self.southeast.query(range)
        
        return found
    
    def draw(self, screen):
        """ Draws the quadtree """
        pygame.draw.rect(screen, (255, 255, 0), self.boundary, 1)

        if self.divided:
            self.northwest.draw(screen)
            self.northeast.draw(screen)
            self.southwest.draw(screen)
            self.southeast.draw(screen)
    
    def clear(self, object_type):
        """ Clears the specified object type from the quadtree """
        # Remove player instances from the game_objects list
        self.game_objects = [game_object for game_object in self.game_objects if not isinstance(game_object, object_type)]
        if self.divided:
            self.northwest.clear(object_type)
            self.northeast.clear(object_type)
            self.southwest.clear(object_type)
            self.southeast.clear(object_type)
        
    def __str__(self):
        return f"QuadTree: {self.boundary}, {self.capacity}"
