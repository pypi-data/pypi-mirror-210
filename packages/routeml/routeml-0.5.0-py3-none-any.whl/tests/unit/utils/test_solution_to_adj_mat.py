import unittest
import numpy as np
from routeml.utils import solution_to_adjacency_matrix, get_random_solution, column_normalize_adjacency_matrix

class TestSolutionToAdjacencyMatrix(unittest.TestCase):
    def test_cvrp_solution_to_adjacency_matrix(self):
        cvrp_solution = [0, 1, 2, 3, 4, 0, 5, 6, 7, 0]
        expected_matrix = np.array([[0, 1, 0, 0, 1, 1, 0, 1],
                                    [1, 0, 1, 0, 0, 0, 0, 0],
                                    [0, 1, 0, 1, 0, 0, 0, 0],
                                    [0, 0, 1, 0, 1, 0, 0, 0],
                                    [1, 0, 0, 1, 0, 0, 0, 0],
                                    [1, 0, 0, 0, 0, 0, 1, 0],
                                    [0, 0, 0, 0, 0, 1, 0, 1],
                                    [1, 0, 0, 0, 0, 0, 1, 0]])

        result = solution_to_adjacency_matrix(cvrp_solution)
        np.testing.assert_array_equal(result, expected_matrix)

    def test_check_all_rows_sum_to_2(self):
        for i in range(10):
            cvrp_solution = get_random_solution(50)
            result = solution_to_adjacency_matrix(cvrp_solution)
            num_zeros = np.sum(np.array(cvrp_solution) == 0)
            # Check if all rows except the first row sum to 2
            for i in range(1, result.shape[0]):
                row_sum = np.sum(result[i])
                self.assertIn(row_sum, [1, 2], f"Row {i} does not sum to 1 or 2.")

    def test_column_normalize_adj_mat(self):
        cvrp_solution = get_random_solution(50)
        result = solution_to_adjacency_matrix(cvrp_solution)
        result = column_normalize_adjacency_matrix(result)
        np.testing.assert_array_almost_equal(np.sum(result, axis=0), np.ones(result.shape[0]))

if __name__ == '__main__':
    unittest.main()
