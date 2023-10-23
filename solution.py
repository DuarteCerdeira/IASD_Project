import numpy as np

import search   

class FleetProblem(search.Problem):
    # state: requests, vehicles
    # vehicle: capacity, position, time, requests
    # request: time, origin, destination, passengers, id
    
    def __init__(self):
        self.costs = np.array([])
        self.requests = ()
        self.initial = ()
        self.goal = None
        super().__init__(self.initial, self.goal)

    def load(self, fh):
        """Loads a problem from the opened file object fh."""
        lines = fh.readlines()
        requests = []
        vehicles = []

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
                for i in range(n_requests):
                    aux_parts = lines.pop(0).split()
                    t = float(aux_parts[0])
                    o, d, n = map(int, aux_parts[1:])
                    requests.append((t, o, d, n, i)) # time, origin, destination, passengers, id

            elif line.startswith('V'):
                n_vehicles = int(line.split()[1])
                for i in range(n_vehicles):
                    vehicles.append((int(lines.pop(0)), 0, 0, ())) # capacity, position, time, requests
                    
        requests = tuple(requests)
        vehicles = tuple(vehicles)
        self.initial = (requests, vehicles)
        self.requests = requests

    def path_cost(self, c, state1, action, state2):
        """Return the cost of a solution path that arrives at
        state2 from state1 via action, assuming cost c to get
        up to state1. If the problem is such that the path doesn't
        matter, this function will only look at state2."""
        type, v_id, r_id, time = action  # action, vehicle, request, time
        v_in_1 = state1[1][v_id]
        v_in_2 = state2[1][v_id]
        travel_time = time - v_in_1[2]

        if type == 'Pickup':
            request = tuple(filter(lambda x: x[4] == r_id, state1[0]))[0]
            c += time - request[0]
            for r in v_in_1[3]:
                c += travel_time

        if type == 'Dropoff':
            request = tuple(filter(lambda x: x[4] == r_id, v_in_1[3]))[0]
            c -= self.costs[request[1]][request[2]]
            for r in v_in_1[3]:
                c += travel_time

        return c
        

    def cost(self, sol):
        """Compute cost of solution sol."""
        delays = []
        for s in sol:
            a, _, r, t = s  # action, vehicle, request, time
            if a == 'Dropoff':
                T_od = self.costs[self.initial[0][r][1]][self.initial[0][r][2]]
                delays.append(t - self.initial[0][r][0] - T_od)

        return sum(delays)

    def result(self, old_state, action):
        """Return the state that results from executing
        the given action in the given state."""
        r_list = list(old_state[0])
        v_list = list(old_state[1])
        task, v_id, r_id, time = action

        vehicle = list(v_list[v_id])
        vehicle[3] = list(vehicle[3])
        
        if task == 'Pickup':
            request = tuple(filter(lambda x: x[4] == r_id, r_list))[0]
            vehicle[0] -= request[3]
            vehicle[1] = request[1]
            vehicle[2] = time
            vehicle[3].append(request)
            r_list = list(filter(lambda x: x[4] != r_id, r_list))
            
        elif task == 'Dropoff':
            request = tuple(filter(lambda x: x[4] == r_id, vehicle[3]))[0]
            vehicle[0] += request[3]
            vehicle[1] = request[2]
            vehicle[2] = time
            vehicle[3] = tuple(filter(lambda x: x[4] != r_id, vehicle[3]))

        vehicle[3] = tuple(vehicle[3])
        v_list[v_id] = tuple(vehicle)

        v_list = tuple(v_list)
        r_list = tuple(r_list)
        new_state = (r_list, v_list)
        
        return new_state
    
    def actions(self, state):
        """Return the actions that can be executed in
        the given state."""
        action_list = []
        r_list = state[0]
        v_list = state[1]

        for r in r_list:
            for v_i, v in reversed(list(enumerate(v_list))):
                if(v[0] >= r[3]):
                    time = max(r[0], v[2] + self.costs[v[1]][r[1]])
                    action_list.append(('Pickup', v_i, r[4], time))
            
        for v_i, v in enumerate(v_list):
            for r in v[3]:
                time = v[2] + self.costs[v[1]][r[2]]
                action_list.append(('Dropoff', v_i, r[4], time))
        
        return tuple(action_list)

    def goal_test(self, state):
        """Return True if the state is a goal."""
        # Check if all request lists are empty       
        if all(not v[3] for v in state[1]) and not state[0]:
            return True
        else:
            return False
    
    def h(self, node):
        state = node.state
        remaining_requests_time = sum(self.costs[r[1]][r[2]] for r in state[0])
        T_od = 0    # T_od = sum of all T_od for all requests in all vehicles
        
        for v in state[1]:
            for r in v[3]:
                T_od += self.costs[r[1]][r[2]]  

        # Combine these factors to estimate the remaining cost and
        # weight to not overshadow the cost so far
        heuristic_cost = (remaining_requests_time + T_od) * 0.8
        
        return heuristic_cost
    
    def solve(self):
        """Calls the uninformed search algorithm
        chosen. Returns a solution using the specified format."""
        node = search.astar_search(self, self.h)
        return node.solution()
        
