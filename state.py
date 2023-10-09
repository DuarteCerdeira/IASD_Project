import numpy as np

class State:
    def __init__(self):
        self.open_requests = []  #List of requests
        self.costs = np.array([])   #Matrix of costs
        self.vehicles = []  #List of vehicles
        
    def add_vehicle(self, max_capacity, id):
        """Adds a vehicle to the list of vehicles"""
        vehicle = Vehicle(max_capacity, id)
        self.vehicles.append(vehicle)
        
    def add_request(self, time, origin, destination, passengers, id):
        """Adds a request to the list of requests"""
        request = Request(time, origin, destination, passengers, id)
        self.open_requests.append(request)
        
class Action:
    def __init__(self, action_type, v_id, req_id, time):
        self.action_type = action_type    #Type of action
        self.v_id = v_id  #ID of the vehicle
        self.req_id = req_id  #ID of the request
        self.time = time    #Time of the action
        
    def __str__(self):
        return f'{self.action_type}, {str(self.v_id)}, {str(self.req_id)}, {str(self.time)}'
        
class Request:
    def __init__(self, time, origin, destination, passengers, id):
        self.time = time    #Time of the request
        self.origin = origin    #Origin point of the request
        self.destination = destination  #Destination of the request
        self.passengers = passengers    #Number of passengers
        self.id = id    #ID of the request

class Vehicle:
    def __init__(self, max_capacity, id):
        self.position = 0   #Position of the vehicle
        self.occupation = 0 #Number of passengers in the vehicle
        self.current_time = 0   #Current time of the vehicle
        self.requests = []  #List of requests
        self.max_capacity = max_capacity    #Max capacity of the vehicle
        self.id = id    #ID of the vehicle