import unittest
from routeml.utils import get_route_demand

class TestGetRouteDemand(unittest.TestCase):
    def test_get_route_demand(self):
        routes = [[0, 1, 2, 0], [0, 3, 4, 0], [0, 5, 6, 7, 0]]
        demand = {0: 0, 1: 10, 2: 20, 3: 15, 4: 25, 5: 30, 6: 5, 7: 8}

        total_demand = get_route_demand(routes, demand)
        self.assertEqual(total_demand, [30, 40, 43])

    def test_get_route_demand_empty_routes(self):
        routes = []
        demand = {0: 0, 1: 10, 2: 20}

        total_demand = get_route_demand(routes, demand)
        self.assertEqual(total_demand, [])

    def test_get_route_demand_empty_demand(self):
        routes = [[0, 1, 2, 0], [0, 3, 4, 0]]
        demand = {}

        with self.assertRaises(Exception) as context:
            total_demand = get_route_demand(routes, demand)
        
        self.assertEqual(str(context.exception), "Node 0 not found in the demand dictionary")

    def test_get_route_demand_zero_demand(self):
        routes = [[0, 1, 2, 0], [0, 3, 4, 0]]
        demand = {0: 0, 1: 0, 2: 0, 3: 0, 4: 0}

        total_demand = get_route_demand(routes, demand)
        self.assertEqual(total_demand, [0, 0])

    def test_get_route_demand_with_missing_node(self):
        routes = [[1, 2, 3], [4, 5, 6]]
        demand = {1: 10, 2: 20, 4: 15, 6: 30}
        
        with self.assertRaises(Exception) as context:
            total_demand = get_route_demand(routes, demand)
        
        self.assertEqual(str(context.exception), "Node 3 not found in the demand dictionary")

if __name__ == '__main__':
    unittest.main()
