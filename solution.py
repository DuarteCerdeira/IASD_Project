import numpy as np
import os
from copy import deepcopy

import cProfile
import pstats

import search

def get_from_id(id, aux_l):
    return next(x for x in aux_l if x.id == id)

def pop_from_id(id, aux_l):
    for i, x in enumerate(aux_l):
        if x.id == id:
            return aux_l.pop(i)

class State:
    def __init__(self):
        self.open_requests = []  #List of requests
        self.vehicles = []  #List of vehicles
        
    def add_vehicle(self, max_capacity, id):
        """Adds a vehicle to the list of vehicles"""
        vehicle = Vehicle(max_capacity, id)
        self.vehicles.append(vehicle)
        
    def add_request(self, time, origin, destination, passengers, id):
        """Adds a request to the list of requests"""
        request = Request(time, origin, destination, passengers, id)
        self.open_requests.append(request)
    
    def __str__(self) -> str:
        return f'Vehicles: {str(self.vehicles)}\nRequests: {str(self.open_requests)}'

    def __lt__(self, other):
        return True
        
class Request:
    def __init__(self, time, origin, destination, passengers, id):
        self.time = time    #Time of the request
        self.origin = origin    #Origin point of the request
        self.destination = destination  #Destination of the request
        self.passengers = passengers    #Number of passengers
        self.id = id    #ID of the request
        
    def __str__(self) -> str:
        return f'ID {str(self.id)}: {str(self.time)}, {str(self.origin)}, {str(self.destination)}, {str(self.passengers)}\n'

class Vehicle:
    def __init__(self, max_capacity, id):
        self.pos = 0   #Position of the vehicle
        self.occupation = 0 #Number of passengers in the vehicle
        self.current_time = 0   #Current time of the vehicle
        self.req = []  #List of requests
        self.max_capacity = max_capacity    #Max capacity of the vehicle
        self.id = id    #ID of the vehicle
        
    def __str__(self) -> str:
        return f'Vehicle {str(self.id)}: req->{str(self.req)}, pos:{str(self.pos)}, occupation:{str(self.occupation)}'

class FleetProblem(search.Problem):
    def __init__(self, initial=None, goal=None):
        super().__init__(initial, goal)
        self.initial = State() if initial is None else initial
        self.costs = np.array([])

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
                for i in range(n_requests):
                    aux_parts = lines.pop(0).split()
                    t = float(aux_parts[0])
                    o, d, n = map(int, aux_parts[1:])
                    self.initial.add_request(t, o, d, n, i)

            elif line.startswith('V'):
                n_vehicles = int(line.split()[1])
                for i in range(n_vehicles):
                    self.initial.add_vehicle(int(lines.pop(0)), i)

    def path_cost(self, c, state1, action, state2):
        """Return the cost of a solution path that arrives at
        state2 from state1 via action, assuming cost c to get
        up to state1. If the problem is such that the path doesn't
        matter, this function will only look at state2."""
        type, vehicle, req, time = action  # action, vehicle, request, time
        v_in_1 = get_from_id(vehicle, state1.vehicles)
        v_in_2 = get_from_id(vehicle, state2.vehicles)

        if type == 'Pickup':
            request = get_from_id(req, state1.open_requests)
            c += time + self.costs[v_in_2.pos][request.destination] - (request.time + self.costs[request.origin][request.destination])
            # c += time - request.time

        c += self.costs[v_in_1.pos][v_in_2.pos] * len(v_in_1.req)

        if type == 'Dropoff':
            c -= self.costs[v_in_1.pos][v_in_2.pos]

        for r in v_in_2.req:
            c += self.costs[v_in_2.pos][r.destination] - self.costs[v_in_1.pos][r.destination]

        return c
        

    def cost(self, sol):
        """Compute cost of solution sol."""
        delays = []
        for s in sol:
            a, _, r, t = s  # action, vehicle, request, time
            if a == 'Dropoff':
                T_od = self.costs[self.initial.open_requests[r].origin][self.initial.open_requests[r].destination]
                delays.append(t - self.initial.open_requests[r].time - T_od)

        return sum(delays)

    def result(self, old_state, type):
        """Return the state that results from executing
        the given action in the given state."""
        state=deepcopy(old_state)
        type, vehicle, req, time = type  # action, vehicle, request, time
        vehicle = get_from_id(vehicle, state.vehicles)
        vehicle.current_time = time
        
        if type == 'Pickup':
            req = get_from_id(req, state.open_requests)
            vehicle.pos = req.origin
            vehicle.occupation += req.passengers
            vehicle.req.append(pop_from_id(req.id, state.open_requests))
            
        elif type == 'Dropoff':
            req = get_from_id(req, vehicle.req)
            vehicle.pos = req.destination
            vehicle.occupation -= req.passengers
            pop_from_id(req.id, vehicle.req)
        
        return state
    
    def actions(self, state):
        """Return the actions that can be executed in
        the given state."""
        action_list = set()  # Use a set for faster membership checks
        for v in state.vehicles:
            for r in state.open_requests:
                if v.occupation + r.passengers <= v.max_capacity:
                    time = max(r.time, v.current_time + self.costs[v.pos][r.origin])
                    action_list.add(('Pickup', v.id, r.id, time))

            for r in v.req:
                time = v.current_time + self.costs[v.pos][r.destination]
                action_list.add(('Dropoff', v.id, r.id, time))

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
    filename = "ex2.dat"

    file_path = os.path.join('tests', filename)
    with open(file_path) as fh:
        prob.load(fh)

    cProfile.run('prob.solve()', 'output.prof')
    p = pstats.Stats('output.prof')
    p.sort_stats('cumulative').print_stats(20)
    sol = prob.solve()
    print(sol)  
    print(prob.cost(sol))
