import pygame
from components.particle import Particle
from components.utilities.boundary_shape import BoundaryShape, Circle, Rectangle
from pygame.locals import *
from pygame.math import Vector2


class QuadTree:
    def __init__(self, boundary: Rectangle, capacity: int):
        self.boundary = boundary
        self.max_particles = capacity
        self.particles = []
        self.divided = False
        self.depth = 10

    
    def __str__(self):
        """Return a string representation of this node, suitably formatted."""
        sp = ', '
        s = str(self.boundary)
        if self.particles:
            s += sp + ', '.join(str(particle) for particle in self.particles)

        if not self.divided:
            return s
        regions = '\n'.join(
            [
                'nw: ' + str(self.nw) + sp, \
                'ne: ' + str(self.ne) + sp, \
                'se: ' + str(self.se) + sp, \
                'sw: ' + str(self.sw)
            ]
        )
        final = f"{s}\n" + regions
        return final

    def insert(self, particle: Particle):
        """ Inserts a game object into the quadtree
        
        Args:
            object_data (tuple): A tuple of (x, y, radius) coordinates and radius.
        
        Returns:
            bool: True if the game object was inserted, False otherwise.
        """
        if not self.boundary.contains(particle):
            return False
        
        if len(self.particles) < self.max_particles:
            self.particles.append(particle)
            return True

        if not self.divided:
            self.divide()
        if self.nw.insert(particle):
            return True
        if self.ne.insert(particle):
            return True
        if self.sw.insert(particle):
            return True
        if self.se.insert(particle):
            return True
        return False
    
    def remove(self, particle: Particle):
        """ Removes a game object from the quadtree """
        if particle in self.particles:
            self.particles.remove(particle)
            return True
        elif self.divided:
            if self.nw.remove(particle):
                return True
            elif self.ne.remove(particle):
                return True
            elif self.sw.remove(particle):
                return True
            elif self.se.remove(particle):
                return True
        return False

    def divide(self):
        """ Divides the quadtree into four quadtrees """
        x = self.boundary.position.x
        y = self.boundary.position.y
        w = self.boundary.w / 2
        h = self.boundary.h / 2
        child_size = Vector2(w, h)

        nw = Rectangle(Vector2(x, y), child_size)
        ne = Rectangle(Vector2(x + w, y), child_size)
        sw = Rectangle(Vector2(x, y + h), child_size)
        se = Rectangle(Vector2(x + w, y + h), child_size)

        self.nw = QuadTree(nw, self.max_particles)
        self.ne = QuadTree(ne, self.max_particles)
        self.sw = QuadTree(sw, self.max_particles)
        self.se = QuadTree(se, self.max_particles)

        self.divided = True

    def query(self, boundary: BoundaryShape):

        particles = []

        if boundary.intersects(self.boundary):
            return particles

        # ... and if this node has children, search them too.
        if self.divided:
            particles += self.nw.query(boundary)
            particles += self.ne.query(boundary)
            particles += self.sw.query(boundary)
            particles += self.se.query(boundary)
        
        # Search this node's points to see if they lie within boundary ...
        for particle in self.particles:
            if boundary.contains(particle):
                particles.append(particle)
        
        return self.get_particles_ordered(particles)

    def get_particles_ordered(self, particles):
        # Sort particles by id integer
        particles.sort(key=lambda particle: str(particle.id))

        return particles
    
    def draw(self, screen):
        """ Draws the quadtree """
        self.boundary.draw(screen)
        if self.divided:
            self.nw.draw(screen)
            self.ne.draw(screen)
            self.sw.draw(screen)
            self.se.draw(screen)
    
    def clear(self, object_type):
        """ Clears the specified object type from the quadtree """
        # Remove player instances from the object_datas list
        self.particles = [object_data for object_data in self.particles if not isinstance(object_data, object_type)]
        if self.divided:
            self.nw.clear(object_type)
            self.ne.clear(object_type)
            self.sw.clear(object_type)
            self.se.clear(object_type)

    def __len__(self):
        """Return the number of points in the quadtree."""

        npoints = len(self.particles)
        if self.divided:
            npoints += len(self.nw)+len(self.ne)+len(self.se)+len(self.sw)
        return npoints