import numpy as np

# import search

class FleetProblem():
    def __init__(self) -> None:
        self.requests = []
        self.costs = np.array([])
        self.vehicles = []
        self.n_vehicles = 0
        self.n_points = 0
        self.n_requests = 0

    def load(self, fh):
        """Loads a problem from the opened file object fh."""
        lines = fh.readlines()
        for line in lines:
            if line.startswith('#'):
                continue
            # Line that starts with 'P' contains the number of points
            if line.startswith('P'):
                self.n_points = int(line.split()[1])

                # The following n_points - 1 lines contain the costs between each pair of points
                self.costs = np.zeros((self.n_points, self.n_points))
                for i in range(self.n_points - 1):
                    self.costs[i, i+1:] = np.array([int(x) for x in lines[lines.index(line) + i + 1].split()])
                    self.costs[i+1:, i] = self.costs[i, i+1:]
                
            # Line that starts with 'R' contains the number of requests
            elif line.startswith('R'):
                self.n_requests = int(line.split()[1])

                # The following n_requests lines contain the requests
                for i in range(self.n_requests):
                    t, o, d, n = [int(x) for x in lines[lines.index(line) + i + 1].split()]
                    self.requests.append({'Time': t, 'Origin': o, 'Destination': d, 'Number of Passangers': n})

            # Line that starts with 'V' contains the number of vehicles
            elif line.startswith('V'):
                self.n_vehicles = int(line.split()[1])

                # The following n_vehicles lines contain the vehicles capacity
                self.vehicles = []
                for i in range(self.n_vehicles):
                    self.vehicles.append(int(lines[lines.index(line) + i + 1]))

    def cost(self, sol):
        """Compute cost of solution sol."""
        for s in sol:
            a, v, r, t = s  # action, vehicle, request, time
            if a == 'Dropoff':
                T_od = self.costs[self.requests[r]['Origin']][self.requests[r]['Destination']]
                self.requests[r]['Delay'] = t - self.requests[r]['Time'] - T_od

        return sum([r['Delay'] for r in self.requests if 'Delay' in r])
        