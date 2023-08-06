import unittest
import numpy as np
from routeml.utils import get_logit_mask

class TestGetLogitMask(unittest.TestCase):
    def test_get_logit_mask_1(self):
        sol = [0, 1, 2, 0, 3, 4]
        demands = np.array([0, 5, 8, 3, 6])
        capacity = 15
        expected_mask = np.array([[-np.inf, 0., 0., 0., 0.],
                [0., -np.inf, 0., 0., 0.],
                [0., -np.inf, -np.inf, -np.inf, -np.inf],
                [-np.inf, -np.inf, -np.inf, 0., 0.],
                [0., -np.inf, -np.inf, -np.inf, 0.],
                [0., -np.inf, -np.inf, -np.inf, -np.inf]])

        result_mask = get_logit_mask(sol, demands, capacity)

        np.testing.assert_array_equal(result_mask, expected_mask)

if __name__ == '__main__':
    unittest.main()
