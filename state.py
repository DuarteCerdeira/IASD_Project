import numpy as np

def get_from_id(id, aux_l):
    return list(filter(lambda x: x.id == id, aux_l))[0]

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
    