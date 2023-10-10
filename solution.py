import numpy as np
import os
from copy import deepcopy

import search
from state import State, Action, get_from_id, pop_from_id

class FleetProblem(search.Problem):
    def __init__(self, initial, goal=None):
        super().__init__(initial, goal)
        self.initial = State()

    def load(self, fh):
        """Loads a problem from the opened file object fh."""
        lines = fh.readlines()

        while lines != []:
            line = lines.pop(0)

            if line.startswith('#'):
                continue

            elif line.startswith('P'):
                n_points = int(line.split()[1])
                self.initial.costs = np.zeros((n_points, n_points))
                for i in range(n_points - 1):
                    cost_line = lines.pop(0)
                    self.initial.costs[i, i + 1:] = np.array(cost_line.split(), float)
                    self.initial.costs[i + 1:, i] = self.initial.costs[i, i + 1:]

            elif line.startswith('R'):
                n_requests = int(line.split()[1])
                for i in range(n_requests):
                    aux_parts = lines.pop(0).split()
                    t = float(aux_parts[0])
                    o, d, n = map(int, aux_parts[1:])
                    self.initial.add_request(t, o, d, n, i)
                    
            elif line.startswith('V'):
                n_vehicles = int(line.split()[1])
                for i in range(n_vehicles):
                    self.initial.add_vehicle(int(lines.pop(0)), i)

    def cost(self, sol):
        """Compute cost of solution sol."""
        for s in sol:
            a, _, r, t = s  # action, vehicle, request, time
            if a == 'Dropoff':
                T_od = self.initial.costs[self.initial.open_requests[r]['Origin']][self.initial.open_requests[r]['Destination']]
                self.initial.open_requests[r]['Delay'] = t - self.initial.open_requests[r]['Time'] - T_od

        return sum([r['Delay'] for r in self.initial.open_requests if 'Delay' in r])

    def result(self, old_state, action):
        """Return the state that results from executing
        the given action in the given state."""
        state=deepcopy(old_state)
        v = get_from_id(action.v_id, state.vehicles)
        v.current_time = action.time
        
        if action.type == 'Pickup':
            req = get_from_id(action.req_id, state.open_requests)
            v.pos = req.origin
            v.occupation += req.passengers
            v.req.append(pop_from_id(req.id, state.open_requests))
            
        elif action.type == 'Dropoff':
            req = get_from_id(action.req_id, v.req)
            v.pos = req.destination
            v.occupation -= req.passengers
            pop_from_id(req.id, v.req)
        
        return state
    
    def actions(self, state):
        """Return the actions that can be executed in
        the given state."""
        action_list = []
        for v in state.vehicles:
            for r in state.open_requests:
                if(v.occupation + r.passengers <= v.max_capacity):
                    time=max(r.time, v.current_time + state.costs[v.pos][r.origin])
                    action_list.append(Action('Pickup', v.id, r.id, time))
            
            for r in v.req:
                time=v.current_time + state.costs[v.pos][r.destination]
                action_list.append(Action('Dropoff', v.id, r.id, time))
        
        return action_list

    def goal_test(self, state):
        """Return True if the state is a goal."""
        #check if all request lists are empty       
        if all(not v.req for v in state.vehicles) and not state.open_requests:
            return True
        else:
            return False
    
    def solve(self):
        """Calls the uninformed search algorithm
        chosen. Returns a solution using the specified format."""
        node = search.uniform_cost_search(self)
        return node.solution()
        

if __name__=="__main__":
    prob = FleetProblem(None)
    filename = "ex10.dat"

    file_path = os.path.join('tests', filename)
    with open(file_path) as fh:
        prob.load(fh)

    prob.solve()
        