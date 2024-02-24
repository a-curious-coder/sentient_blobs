import pygame
from pygame.math import Vector2

from .particle import Particle


class BoundaryShape:
    def __init__(self, position: Vector2):
        self.position = position
        self.color = (255, 255, 255)
        self.line_thickness = 1


class Rectangle(BoundaryShape):
    def __init__(self, position: Vector2, size: Vector2):
        """
        Initializes a Rectangle object.

        Args:
            position (Vector2): The position of the top-left corner of the rectangle.
            size (Vector2): The width and height of the rectangle.
        """
        super().__init__(position)
        self.size = size
        self.x, self.y = position
        self.w, self.h = size

    def contains(self, particle: Particle) -> bool:
        """
        Checks if a particle center is contained within the rectangle.

        Args:
            particle (Particle): The particle to check.

        Returns:
            bool: True if the particle is contained within the rectangle, False otherwise.
        """
        x, y = particle.position
        bx, by = self.position
        w, h = self.size
        if x >= bx and x <= bx+w and y >= by and y <= by+h:
            return True
        else:
            return False

    def intersects(self, other: BoundaryShape) -> bool:
        """
        Checks if the rectangle intersects with another rectangle.

        Args:
            range (Rectangle): The other rectangle to check.

        Returns:
            bool: True if the rectangles intersect, False otherwise.
        """
        xr, yr = other.position
        wr, hr = other.size
        if xr > self.x + self.w or \
            xr + wr < self.x-self.w or \
            yr > self.y + self.h or \
            yr + hr < self.y-self.h:
            return True
        else:
            return False

    def draw(self, screen: pygame.Surface, colour = (255, 255, 255)):
        """
        Draws the rectangle on the screen.

        Args:
            screen (pygame.Surface): The surface to draw on.
        """
        pygame.draw.rect(screen, colour, [self.x, self.y, self.w, self.h], self.line_thickness)
    
    def __str__(self):
        return f"Rectangle: {self.position}, {self.size}"

class Circle(BoundaryShape):
    def __init__(self, position, radius):
        super().__init__(position) 
        self.radius = radius
        self.sqradius = self.radius * self.radius

    def contains(self, particle: Particle) -> bool:
        x1, y1 = self.position
        x2, y2 = particle.position
        dist = pow(x2-x1, 2) + pow(y2-y1, 2)
        if dist <= self.sqradius:
            return True
        else:
            return False

    def intersects(self, _range: BoundaryShape) -> bool:
        x1, y1 = self.position
        x2, y2 = _range.position
        w, h = _range.size
        r = self.radius
        dist_x, dist_y = abs(x2-x1), abs(y2-y1)

        edges = pow(dist_x-w, 2) + pow(dist_y-h, 2)

        if dist_x > (r+w) or dist_y > (r+h):
            return False

        if dist_x <= w or dist_y <= h:
            return True

        return (edges <= self.sqradius)

    def draw(self, screen: pygame.Surface):
        pygame.draw.circle(screen, self.color, self.position, self.radius, self.lineThickness)
