import unittest
import requests
import tempfile
import os
from routeml.utils import parse_vrplib_solution


class VRPSolutionParserTestCase(unittest.TestCase):
    def test_parse_solution_from_url(self):
        solution_url = 'http://vrp.atd-lab.inf.puc-rio.br/media/com_vrp/instances/Li/Li_22.sol'
        response = requests.get(solution_url)
        solution_text = response.text
        # Create a temporary directory
        with tempfile.TemporaryDirectory() as temp_dir:
            file_path = os.path.join(temp_dir, "Li_22.sol")

            # Write the file content to the temporary directory
            with open(file_path, "w") as file:
                file.write(solution_text)

            routes, cost = parse_vrplib_solution(file_path)

            # Perform assertions on the parsed routes and cost
            self.assertEqual(len(routes), 15)
            self.assertEqual(cost, 14499.04468)

            # Additional assertions or validations on the parsed data

            print("VRP solution parsed successfully!")


if __name__ == '__main__':
    unittest.main()
