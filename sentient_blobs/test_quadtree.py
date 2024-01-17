
import unittest

from components.particle import Particle
from components.utilities.boundary_shape import Rectangle
from components.utilities.quadtree import QuadTree
from pygame.math import Vector2


class TestQuadTree(unittest.TestCase):
    def setUp(self):
        self.boundary = Rectangle(Vector2(0, 0), Vector2(100, 100))
        self.tree = QuadTree(self.boundary, 1)
        self.particle = Particle("Test", Vector2(25, 50), 2, (255, 255, 255))
        self.particle_2 = Particle("Test2", Vector2(75, 50), 2, (255, 255, 255))

    def test_insert(self):
        self.assertTrue(self.tree.insert(self.particle))
        # Evaluate whether the particle is in the tree
        self.assertTrue(self.tree.particles[0] == self.particle)

    def test_remove(self):
        self.tree.insert(self.particle)
        self.assertTrue(self.tree.remove(self.particle))
        self.assertFalse(self.tree.particles)

    def test_str(self):
        self.assertEqual(str(self.tree), "Rectangle: [0, 0], [100, 100]")
    
    def test_str_with_particles(self):
        self.tree.insert(self.particle)
        self.tree.insert(self.particle_2)

        actual = str(self.tree)
        # Quadtree should have subdivided into four regions and the particles should be in the NE regions
        expected = "Rectangle: [0, 0], [100, 100], Test\nnw: Rectangle: [0, 0], [50, 50], \nne: Rectangle: [50, 0], [50, 50], Test2, \nse: Rectangle: [50, 50], [50, 50], \nsw: Rectangle: [0, 50], [50, 50]"
        
        self.assertEqual(actual, expected)

    def test_query(self):
        # Create five particles
        particles = [Particle(f"Test_{i}", Vector2(25, 50), 2, (255, 255, 255)) for i in range(5)]
        for particle in particles:
            self.tree.insert(particle)

        actual = self.tree.query(self.boundary)
        expected = [particle for particle in particles]

        self.assertEqual(actual, expected)

    
if __name__ == "__main__":
    unittest.main()