import numpy as np
import hygese as hgs
from scipy.spatial import distance_matrix

def hgs_solve(coords, demands, capacity, time_limit=5):
    """
    coords: a numpy array of coordinates, where each row represents the x and y coordinates of a node
    demands: a numpy array of demands, where index 0 represents the demand of the depot (0)
    capacity: integer, capacity of all vehicles
    time_limit: integer, maximum time limit for the solver in seconds
    """

    n = len(coords)
    x = coords[:, 0]
    y = coords[:, 1]

    # Solver initialization
    ap = hgs.AlgorithmParameters(timeLimit=time_limit)
    hgs_solver = hgs.Solver(parameters=ap, verbose=False)

    # Data preparation
    data = dict()
    data['x_coordinates'] = x
    data['y_coordinates'] = y
    data['distance_matrix'] = distance_matrix(coords, coords)
    data['service_times'] = np.zeros(n)
    data['demands'] = demands
    data['vehicle_capacity'] = capacity
    data['num_vehicles'] = 100  # Update with the appropriate number of vehicles
    data['depot'] = 0

    result = hgs_solver.solve_cvrp(data)
    return result
