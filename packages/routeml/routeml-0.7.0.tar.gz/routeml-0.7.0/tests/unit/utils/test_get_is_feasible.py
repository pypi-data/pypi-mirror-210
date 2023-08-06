import unittest
from routeml.utils import is_feasible

class TestIsFeasible(unittest.TestCase):
    def test_is_feasible(self):
        demand = {0: 0, 1: 10, 2: 15, 3: 8, 4: 12}
        capacity = 20

        routes1 = [[0, 1, 2, 3, 0], [0, 4, 0]]
        self.assertFalse(is_feasible(routes1, demand, capacity))

        routes2 = [[0, 1, 0], [0, 2, 0], [0, 3, 0], [0, 4, 0]]
        self.assertTrue(is_feasible(routes2, demand, capacity))

        routes3 = [[0, 1, 2, 4, 0], [0, 3, 0]]
        self.assertFalse(is_feasible(routes3, demand, capacity))

        routes4 = [[0, 1, 3, 0], [0, 2, 4, 0]]
        self.assertFalse(is_feasible(routes4, demand, capacity))

        routes5 = []
        self.assertFalse(is_feasible(routes5, demand, capacity))

        # Single route exceeding capacity
        routes6 = [[0, 1, 2, 3, 4, 0]]
        self.assertFalse(is_feasible(routes6, demand, capacity))

        # Duplicate nodes in a single route
        routes7 = [[0, 1, 2, 2, 3, 0], [0, 4, 0]]
        self.assertFalse(is_feasible(routes7, demand, capacity))

        # Duplicate nodes across routes
        routes8 = [[0, 1, 2, 3, 0], [0, 3, 4, 0]]
        self.assertFalse(is_feasible(routes8, demand, capacity))

        # Nodes not present in demand dictionary
        routes9 = [[0, 1, 2, 5, 0], [0, 3, 4, 0]]
        self.assertFalse(is_feasible(routes9, demand, capacity))

if __name__ == '__main__':
    unittest.main()
