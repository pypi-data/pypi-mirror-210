import unittest
import requests
from routeml.utils import parse_vrplib_file, parse_vrplib_solution, get_cvrp_cost, add_depot_to_routes

class VRPLIBIntegrationTestCase(unittest.TestCase):
    def test_vrplib_integration(self):
        files = [
            [
                "http://vrp.atd-lab.inf.puc-rio.br/media/com_vrp/instances/X/X-n134-k13.vrp",
                "http://vrp.atd-lab.inf.puc-rio.br/media/com_vrp/instances/X/X-n134-k13.sol",
                True
            ],
            [
                "http://vrp.atd-lab.inf.puc-rio.br/media/com_vrp/instances/X/X-n101-k25.vrp",
                "http://vrp.atd-lab.inf.puc-rio.br/media/com_vrp/instances/X/X-n101-k25.sol",
                True
            ],
            [
                "http://vrp.atd-lab.inf.puc-rio.br/media/com_vrp/instances/Li/Li_21.vrp",
                "http://vrp.atd-lab.inf.puc-rio.br/media/com_vrp/instances/Li/Li_21.sol",
                False
            ]
        ]
        for z in files:
            vrp_file_url, vrp_sol_url, uchoa = z
            vrplib_data = parse_vrplib_file(vrp_file_url)
            vrplib_solution, vrplib_cost = parse_vrplib_solution(vrp_sol_url)
            vrplib_solution = add_depot_to_routes(vrplib_solution)

            # 3. Get cost from parsed VRPLIB file
            cost = get_cvrp_cost(vrplib_solution, vrplib_data['node_coords'], uchoa=uchoa)

            # 4. Assert that the cost matches the VRPLIB solution
            self.assertAlmostEqual(vrplib_cost, cost, places=3)


if __name__ == '__main__':
    unittest.main()
