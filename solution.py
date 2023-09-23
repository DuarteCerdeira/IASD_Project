import numpy as np

# import search

class FleetProblem():
    def __init__(self) -> None:
        self.requests = []
        self.vehicles = []

    def load(self, fh):
        """Loads a problem from the opened file object fh."""
        lines = fh.readlines()

        while lines != []:
            line = lines.pop(0)

            if line.startswith('#'):
                continue

            elif line.startswith('P'):
                n_points = int(line.split()[1])
                self.costs = np.zeros((n_points, n_points))
                for i in range(n_points - 1):
                    cost_line = lines.pop(0)
                    self.costs[i, i + 1:] = np.array(cost_line.split(), float)
                    self.costs[i + 1:, i] = self.costs[i, i + 1:]

            elif line.startswith('R'):
                n_requests = int(line.split()[1])
                for _ in range(n_requests):
                    aux_parts = lines.pop(0).split()
                    t = float(aux_parts[0])
                    o, d, n = map(int, aux_parts[1:])
                    self.requests.append({
                        'Time': t, 
                        'Origin': o, 
                        'Destination': d, 
                        'Number of Passengers': n
                        })
                    
            elif line.startswith('V'):
                n_vehicles = int(line.split()[1])
                for _ in range(n_vehicles):
                    self.vehicles.append(int(lines.pop(0)))


    def cost(self, sol):
        """Compute cost of solution sol."""
        total_cost = 0
        for s in sol:
            a, _, r, t = s  # action, vehicle, request, time
            if a == 'Dropoff':
                T_od = self.costs[self.requests[r]['Origin']][self.requests[r]['Destination']]
                total_cost += t - self.requests[r]['Time'] - T_od

        return total_cost