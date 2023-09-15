import numpy as np

# import search

class FleetProblem():
    def load(self, fh):
        """Loads a problem from the opened file object fh."""
        lines = fh.readlines()
        for line in lines:
            if line.startswith('#'):
                continue
            # Line that starts with 'P' contains the number of points
            if line.startswith('P'):
                n_points = int(line.split()[1])

                # The following n_points - 1 lines contain the costs between each pair of points
                costs = np.zeros((n_points, n_points))
                for i in range(n_points - 1):
                    costs[i, i+1:] = np.array([int(x) for x in lines[lines.index(line) + i + 1].split()])
                    costs[i+1:, i] = costs[i, i+1:]
                
            # Line that starts with 'R' contains the number of requests
            elif line.startswith('R'):
                n_requests = int(line.split()[1])

                # The following n_requests lines contain the requests
                requests = []
                for i in range(n_requests):
                    t, o, d, n = [int(x) for x in lines[lines.index(line) + i + 1].split()]
                    requests.append({'Time': t, 'Origin': o, 'Destination': d, 'Number of Passangers': n})

            # Line that starts with 'V' contains the number of vehicles
            elif line.startswith('V'):
                n_vehicles = int(line.split()[1])

                # The following n_vehicles lines contain the vehicles capacity
                vehicles = []
                for i in range(n_vehicles):
                    vehicles.append(int(lines[lines.index(line) + i + 1]))

    def cost(self, sol):
        """Compute cost of solution sol."""
        pass