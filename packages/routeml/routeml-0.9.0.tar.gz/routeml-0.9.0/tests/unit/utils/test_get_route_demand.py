import unittest
from routeml.utils import get_all_route_demands, get_route_demand

class TestGetRouteDemand(unittest.TestCase):
    def test_get_route_demand(self):
        routes = [[0, 1, 2, 0], [0, 3, 4, 0], [0, 5, 6, 7, 0]]
        demand = {0: 0, 1: 10, 2: 20, 3: 15, 4: 25, 5: 30, 6: 5, 7: 8}

        total_demand = get_all_route_demands(routes, demand)
        self.assertEqual(total_demand, [30, 40, 43])

    def test_get_route_demand_empty_routes(self):
        routes = []
        demand = {0: 0, 1: 10, 2: 20}

        total_demand = get_all_route_demands(routes, demand)
        self.assertEqual(total_demand, [])

    def test_get_route_demand_empty_demand(self):
        routes = [[0, 1, 2, 0], [0, 3, 4, 0]]
        demand = {}

        with self.assertRaises(Exception) as context:
            total_demand = get_all_route_demands(routes, demand)
        
        self.assertEqual(str(context.exception), "Node 0 not found in the demand dictionary")

    def test_get_route_demand_zero_demand(self):
        routes = [[0, 1, 2, 0], [0, 3, 4, 0]]
        demand = {0: 0, 1: 0, 2: 0, 3: 0, 4: 0}

        total_demand = get_all_route_demands(routes, demand)
        self.assertEqual(total_demand, [0, 0])

    def test_get_route_demand_with_missing_node(self):
        routes = [[1, 2, 3], [4, 5, 6]]
        demand = {1: 10, 2: 20, 4: 15, 6: 30}
        
        with self.assertRaises(Exception) as context:
            total_demand = get_all_route_demands(routes, demand)
        
        self.assertEqual(str(context.exception), "Node 3 not found in the demand dictionary")

    def test_empty_route(self):
        route = []
        demands = []
        self.assertEqual(get_route_demand(route, demands), 0)

    def test_non_empty_route_positive_demands(self):
        route = [0, 1, 2, 3, 4, 5]
        demands = [0, 10, 5, 8, 12, 3]
        self.assertEqual(get_route_demand(route, demands), 38)

    def test_non_empty_route_zero_demands(self):
        route = [0, 1, 2]
        demands = [0, 0, 0]
        self.assertEqual(get_route_demand(route, demands), 0)

    def test_route_with_duplicate_nodes(self):
        route = [0, 1, 2, 3, 2, 4, 1]
        demands = [0, 5, 3, 2, 4, 6]
        self.assertEqual(get_route_demand(route, demands), 22)

    def test_route_with_negative_demands(self):
        route = [0, 4, 3, 2, 1]
        demands = [0, -10, -5, -8, -12]
        self.assertEqual(get_route_demand(route, demands), -35)

if __name__ == '__main__':
    unittest.main()
