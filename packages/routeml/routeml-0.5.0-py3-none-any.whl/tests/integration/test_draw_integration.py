import unittest
import numpy as np
import matplotlib.pyplot as plt
from routeml.utils import get_cvrp_problem
from routeml.draw import plot_routes
from routeml.solvers import hgs_solve

class CVRPIntegrationTest(unittest.TestCase):
    def test_solve_and_plot_cvrp(self):
        # Generate a CVRP problem
        num_nodes = 100
        node_coords, demands = get_cvrp_problem(num_nodes)

        # Solve the problem using HGS or any other solver
        result = hgs_solve(node_coords, demands, 50, time_limit=2)
        # (Replace with your solver implementation)

        # Obtain the solution routes
        routes = result.routes

        # Plot and save the solution as a PNG file
        plot_routes(routes, node_coords, save_path="test_output/solution.png")

        # Add assertions if needed
        # self.assertEqual(...)

if __name__ == '__main__':
    unittest.main()