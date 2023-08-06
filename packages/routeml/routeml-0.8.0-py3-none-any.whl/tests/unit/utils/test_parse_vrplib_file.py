import unittest
import requests
import os
import tempfile
from routeml.utils import parse_vrplib_file


class VRPLIBParserTestCase(unittest.TestCase):
    def test_parse_vrplib_file(self):
        url = "http://vrp.atd-lab.inf.puc-rio.br/media/com_vrp/instances/X/X-n101-k25.vrp"
        response = requests.get(url)
        content = response.text

        # Create a temporary directory
        with tempfile.TemporaryDirectory() as temp_dir:
            file_path = os.path.join(temp_dir, "X-n101-k25.vrp")

            # Write the file content to the temporary directory
            with open(file_path, "w") as file:
                file.write(content)

            # Perform the parsing using the local file
            parsed_data = parse_vrplib_file(file_path)

            # Perform assertions on the parsed data
            self.assertEqual(parsed_data['name'], "X-n101-k25")
            self.assertEqual(parsed_data['type'], "CVRP")
            self.assertEqual(parsed_data['dimension'], 101)
            self.assertEqual(parsed_data['edge_weight_type'], "EUC_2D")
            self.assertEqual(parsed_data['capacity'], 206)

            self.assertEqual(parsed_data['node_coords'].shape[0], 101)
            self.assertEqual(parsed_data['node_coords'].shape[1], 2)
            self.assertEqual(parsed_data['demand'].shape[0], 101)
            self.assertEqual(len(parsed_data['depot_ids']), 1)

            # Additional assertions or validations on the parsed data

            print("VRPLIB file parsed successfully!")


if __name__ == '__main__':
    unittest.main()
