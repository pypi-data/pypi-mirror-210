import unittest
from routeml.utils import solution_to_routes

class TestSolutionToRoutes(unittest.TestCase):
    def test_solution_to_routes(self):
        solution = [0, 1, 2, 3, 0, 4, 5, 0]
        expected_routes = [[0, 1, 2, 3, 0], [0, 4, 5, 0]]
        routes = solution_to_routes(solution)
        self.assertEqual(routes, expected_routes)

    def test_solution_to_routes_empty_solution(self):
        solution = []
        expected_routes = []
        routes = solution_to_routes(solution)
        self.assertEqual(routes, expected_routes)

    def test_solution_to_routes_single_route(self):
        solution = [0, 1, 2, 3, 4, 0]
        expected_routes = [[0, 1, 2, 3, 4, 0]]
        routes = solution_to_routes(solution)
        self.assertEqual(routes, expected_routes)

    def test_solution_to_routes_multiple_routes(self):
        solution = [0, 1, 0, 2, 3, 0, 4, 0]
        expected_routes = [[0, 1, 0], [0, 2, 3, 0], [0, 4, 0]]
        routes = solution_to_routes(solution)
        self.assertEqual(routes, expected_routes)

if __name__ == '__main__':
    unittest.main()
