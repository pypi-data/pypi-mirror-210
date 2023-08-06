import unittest
from routeml.utils import routes_to_solution

class TestRoutesToSolution(unittest.TestCase):
    def test_routes_to_solution(self):
        routes = [[0, 1, 2, 3, 0], [0, 4, 5, 6, 0]]
        expected_solution = [0, 1, 2, 3, 0, 4, 5, 6, 0]
        solution = routes_to_solution(routes)
        self.assertEqual(solution, expected_solution)

    def test_routes_to_solution_empty_routes(self):
        routes = []
        expected_solution = []
        solution = routes_to_solution(routes)
        self.assertEqual(solution, expected_solution)

    def test_routes_to_solution_single_route(self):
        routes = [[0, 1, 2, 3, 0]]
        expected_solution = [0, 1, 2, 3, 0]
        solution = routes_to_solution(routes)
        self.assertEqual(solution, expected_solution)

    def test_routes_to_solution_multiple_routes(self):
        routes = [[0, 1, 2, 3, 0], [0, 4, 5, 6, 0], [0, 7, 8, 9, 0]]
        expected_solution = [0, 1, 2, 3, 0, 4, 5, 6, 0, 7, 8, 9, 0]
        solution = routes_to_solution(routes)
        self.assertEqual(solution, expected_solution)

if __name__ == '__main__':
    unittest.main()
