import unittest
from evodyn import *

class TestNeighborMethods(unittest.TestCase):

    def test_up(self):
        self.assertEqual(Neighbor.up(0, 3), 2)
        self.assertEqual(Neighbor.up(1, 3), 0)
        self.assertEqual(Neighbor.up(2, 3), 1)

    def test_down(self):
        self.assertEqual(Neighbor.down(0, 3), 1)
        self.assertEqual(Neighbor.down(1, 3), 2)
        self.assertEqual(Neighbor.down(2, 3), 0)

    def test_left(self):
        self.assertEqual(Neighbor.left(0, 4), 3)
        self.assertEqual(Neighbor.left(1, 3), 0)
        self.assertEqual(Neighbor.left(2, 3), 1)

    def test_right(self):
        self.assertEqual(Neighbor.right(0, 4), 1)
        self.assertEqual(Neighbor.right(1, 3), 2)
        self.assertEqual(Neighbor.right(2, 3), 0)

if __name__ == '__main__':
    unittest.main()
