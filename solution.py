import numpy as np
import os
from copy import deepcopy

from state import State, Request, Vehicle, Action
import search

class FleetProblem(search.Problem):
    def __init__(self, initial, goal=None):
        super().__init__(initial, goal)
        self.state = State()

    def load(self, fh):
        """Loads a problem from the opened file object fh."""
        lines = fh.readlines()

        while lines != []:
            line = lines.pop(0)

            if line.startswith('#'):
                continue

            elif line.startswith('P'):
                n_points = int(line.split()[1])
                self.state.costs = np.zeros((n_points, n_points))
                for i in range(n_points - 1):
                    cost_line = lines.pop(0)
                    self.state.costs[i, i + 1:] = np.array(cost_line.split(), float)
                    self.state.costs[i + 1:, i] = self.state.costs[i, i + 1:]

            elif line.startswith('R'):
                n_requests = int(line.split()[1])
                for i in range(n_requests):
                    aux_parts = lines.pop(0).split()
                    t = float(aux_parts[0])
                    o, d, n = map(int, aux_parts[1:])
                    self.state.add_request(t, o, d, n, i)
                    
            elif line.startswith('V'):
                n_vehicles = int(line.split()[1])
                for i in range(n_vehicles):
                    self.state.add_vehicle(int(lines.pop(0)), i)

    def cost(self, sol):
        """Compute cost of solution sol."""
        for s in sol:
            a, _, r, t = s  # action, vehicle, request, time
            if a == 'Dropoff':
                T_od = self.state.costs[self.state.open_requests[r]['Origin']][self.state.open_requests[r]['Destination']]
                self.state.open_requests[r]['Delay'] = t - self.state.open_requests[r]['Time'] - T_od

        return sum([r['Delay'] for r in self.state.open_requests if 'Delay' in r])

    def result(self, state, action):
        """Return the state that results from executing
        the given action in the given state."""
        new_state = deepcopy(state)
        v = new_state.vehicles[action.v_id]
        v.current_time = action.time
        
        if action.type == 'Pickup':
            req = new_state.open_requests[action.req_id]
            v.req.append(req)
            v.occupation += req.passengers
            if (v.pos == req.origin):   #if vehicle is in the origin point (i dont know if this is necessary)  # noqa: E501
                v.pos = req.destination
            new_state.open_requests.pop(action.req_id)
        
        elif action.type == 'Dropoff':
            req = v.req[action.req_id]
            v.pos = v.req[action.req_id].destination
        
        state = new_state

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
        raise NotImplementedError

if __name__=="__main__":
    prob = FleetProblem(None)
    filename = "ex1.dat"

    file_path = os.path.join('tests', filename)
    with open(file_path) as fh:
        prob.load(fh)
    for a in prob.actions(prob.state):
        print(a)
    print(prob.goal_test(prob.state))
        