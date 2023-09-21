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

            parts = line.split()
            if not parts:
                continue

            key = parts[0]

            if key == '#':
                continue
                
            if key == 'P':
                self.n_points = int(parts[1])
                self.costs = np.zeros((self.n_points, self.n_points))

                for i in range(self.n_points - 1):
                    cost_line = lines[lines.index(line) + i + 1]
                    cost_values = [int(x) for x in cost_line.split()]
                    
                    for j in range(i + 1, self.n_points):
                        self.costs[i, j] = self.costs[j, i] = cost_values[j - i - 1]

            elif key == 'R':
                self.n_requests = int(parts[1])
                self.requests = []

                for i in range(self.n_requests):
                    aux_parts= lines[lines.index(line) + i + 1].split()
                    t, o, d, n = map(int, aux_parts)
                    self.requests.append({'Time': t, 'Origin': o, 'Destination': d, 'Number of Passengers': n})

            elif key == 'V':
                self.n_vehicles = int(parts[1])
                for i in range(self.n_vehicles):
                    aux_parts= lines[lines.index(line) + i + 1].split()
                    self.vehicles = aux_parts
                    


    def cost(self, sol):
        """Compute cost of solution sol."""
        for s in sol:
            a, _, r, t = s  # action, vehicle, request, time
            if a == 'Dropoff':
                T_od = self.costs[self.requests[r]['Origin']][self.requests[r]['Destination']]
                self.requests[r]['Delay'] = t - self.requests[r]['Time'] - T_od

        return sum([r['Delay'] for r in self.requests if 'Delay' in r])
        