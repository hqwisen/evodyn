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

class TestLatticeMethods(unittest.TestCase):

    def test_add_matrix(self):
        l = Lattice(2)
        matrix = l.add_matrix()
        self.assertTrue(matrix is l.current())

    def test_counts_current(self):
        l = Lattice(3)
        m = l.add_matrix()
        self.assertEqual(l.current_counts(0), 9)
        self.assertEqual(l.current_counts(1), 0)
        self.assertEqual(l.current_counts(2), 0)
        m[0, 0], m[0, 1], m[0, 2],m[1, 0], m[2, 2] = 1, 1, 2, 2, 2
        self.assertEqual(l.current_counts(1), 2)
        self.assertEqual(l.current_counts(2), 3)


if __name__ == '__main__':
    unittest.main()
