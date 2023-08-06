import unittest
import numpy as np
from routeml.utils import pad_matrix, get_submatrix

class TestMatrixOperations(unittest.TestCase):
    def test_pad_matrix(self):
        # Test 1: Basic padding
        matrix = np.ones((5, 7))
        new_shape = (10, 9)
        padded_matrix = pad_matrix(matrix, new_shape)
        self.assertEqual(padded_matrix.shape, new_shape)
        self.assertEqual(np.sum(padded_matrix), 35)  # Original sum

        # Test 2: No padding needed
        matrix = np.ones((5, 7))
        new_shape = (5, 7)
        padded_matrix = pad_matrix(matrix, new_shape)
        np.testing.assert_array_equal(padded_matrix, matrix)

        # Test 3: Padding only one dimension
        matrix = np.ones((5, 7))
        new_shape = (5, 9)
        padded_matrix = pad_matrix(matrix, new_shape)
        self.assertEqual(padded_matrix.shape, new_shape)
        self.assertEqual(np.sum(padded_matrix), 35)  # Original sum

    def test_get_submatrix(self):
        matrix = np.arange(500).reshape((10, 50))  # 10x50 matrix
        indices = [1, 3, 5, 7, 9]
        submatrix = get_submatrix(indices, matrix, (10, 100))
        for i, idx in enumerate(indices):
            np.testing.assert_array_equal(submatrix[:, i], matrix[:, idx])

    def test_pad_and_get_submatrix(self):
        N = 1000
        M = 1200
        l_matrix = np.random.rand(7, N)
        l_matrix = pad_matrix(l_matrix, (9, N))
        indices = [1, 3, 5, 7, 9]
        r_matrix = get_submatrix(indices, l_matrix, (9, M))
        for i, idx in enumerate(indices):
            np.testing.assert_array_equal(r_matrix[:, i], l_matrix[:, idx])
        self.assertEqual(np.sum(l_matrix[:, indices]), np.sum(r_matrix[:, :len(indices)]))

if __name__ == '__main__':
    unittest.main()
