import unittest
from routeml.utils import get_cvrp_cost
import math

class TestGetCVRPCost(unittest.TestCase):
    def test_get_cvrp_cost_with_routes(self):
        routes = [[0, 1, 2, 0], [0, 3, 4, 5, 0]]
        coordinates = {0: (0, 0), 1: (1, 1), 2: (2, 2), 3: (3, 3), 4: (4, 4), 5: (5, 5)}

        cost = get_cvrp_cost(routes, coordinates)
        self.assertAlmostEqual(cost, 2 * math.sqrt(50) + 2 * math.sqrt(8))

    def test_get_cvrp_cost_with_solution(self):
        solution = [0, 1, 2, 3, 4, 5, 0]
        coordinates = {0: (0, 0), 1: (1, 1), 2: (2, 2), 3: (3, 3), 4: (4, 4), 5: (5, 5)}

        cost = get_cvrp_cost(solution, coordinates)
        self.assertAlmostEqual(cost, 2 * math.sqrt(50))

    def test_get_cvrp_cost_invalid_input(self):
        invalid_input = "invalid"
        coordinates = {0: (0, 0), 1: (1, 1), 2: (2, 2)}

        with self.assertRaises(ValueError):
            get_cvrp_cost(invalid_input, coordinates)

if __name__ == "__main__":
    unittest.main()
