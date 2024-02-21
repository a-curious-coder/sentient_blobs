
import unittest

from parameterized import parameterized
from pygame.math import Vector2

from sentient_blobs.modules.components.food import Food
from sentient_blobs.modules.components.particle import Particle
from sentient_blobs.modules.components.player import Player
from sentient_blobs.modules.utilities.boundary_shape import Rectangle
from sentient_blobs.modules.utilities.quadtree import QuadTree
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
        self.assertFalse(self.tree.remove(self.particle))

    def test_str(self):
        self.assertEqual(str(self.tree), "Rectangle: [0, 0], [100, 100]")
    
    def test_str_with_particles(self):
        self.tree.insert(self.particle)
        self.tree.insert(self.particle_2)

        actual = str(self.tree)
        # Quadtree should have subdivided into four regions and the particles should be in the NE regions
        expected = "Rectangle: [0, 0], [100, 100], Test\nnw: Rectangle: [0, 0], [50, 50], \nne: Rectangle: [50, 0], [50, 50], Test2, \nse: Rectangle: [50, 50], [50, 50], \nsw: Rectangle: [0, 50], [50, 50]"
        
        self.assertEqual(actual, expected)

    @parameterized.expand([
        ("Player", 5),
        ("Food", 5),
    ])
    def test_query(self, particle_type, num_particles):

        particles = []
        if particle_type == "Player":
            # Create five Players
            particles = [Player(Vector2(25, 50), i) for i in range(num_particles)]
        else:
            particles = [Food(Vector2(25, 50), i) for i in range(num_particles)]

        for particle in particles:
            self.tree.insert(particle)

        ## Make sure to search only for the relevant object
        actual = self.tree.query(self.boundary, particle_type)
        expected = particles

        self.assertEqual(len(actual), len(expected))
        
        for i in range(num_particles):
            self.assertTrue(actual[i] in expected)

if __name__ == "__main__":
    unittest.main()