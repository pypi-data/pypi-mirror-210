import matplotlib.pyplot as plt

def plot_routes(routes, node_coords, save_path):
    # Create a list of unique colors for each route
    colors = ['b', 'g', 'r', 'c', 'm', 'y', 'k']

    # Plot each route with a different color
    for i, route in enumerate(routes):
        x = [node_coords[node][0] for node in route]
        y = [node_coords[node][1] for node in route]
        plt.plot(x, y, 'o-', color=colors[i % len(colors)])

    # Plot the depot node with an X
    depot_x, depot_y = node_coords[0]
    plt.plot(depot_x, depot_y, 'rx', markersize=10, label='Depot')

    plt.xlabel('X')
    plt.ylabel('Y')
    plt.title('Routes')
    plt.savefig(save_path)
    plt.close()
