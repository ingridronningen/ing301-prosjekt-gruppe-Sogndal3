class Measurement:
    """
    This class represents a measurement taken from a sensor.
    """

    def __init__(self, timestamp, value, unit):
        self.timestamp = timestamp
        self.value = value
        self.unit = unit

class device: 
    def __init__(self, device_id, supplier, model_name):
        self.device_id = device_id
        self.supplier = supplier
        self.model_name = model_name
    
    def is_sensor(self): 
        return False
    def is_actuatir(self):
        return False
    def get_device_type(self):
        return "Device"
    
import random
from datetime import datetime

class Sensor (device):
    def __init__(self, device_id, supplier, model_name, unit, sensor_type):
        super().__init__(device_id, supplier, model_name)
        self.unit = unit
        self.sensor_type = sensor_type
    def is_sensor(self):
        return True
    def get_device_type(self):
        return self.sensor_type
    def last_measurement(self): 
        value = round(random.uniform(0, 100), 2)
        timestamp = datetime.now().isoformat()
        return Measurement(timestamp, value, self.unit)
    
class Actuator(device): 
    def __init__(self, device_id, supplier, model_name, actuator_type):
        super().__init__(device_id, supplier, model_name)
        self.actuator_type = actuator_type
        self._active = False
        self.target_value = None
    def is_actuator(self):
        return True
    def get_device_type(self):
        return self.actuator_type
    def turn_on(self,target_value = None): 
        self._active = True
        if target_value is not None: 
            self.target_value = target_value
    def turn_on (self):
        self._active = False
        self.target_value = None
    def is_active (self):
        return self._active

class Floor: 
    def __init__ (self, level): 
        self.level = level 
        self.rooms = []
    def get_area(self): 
        total = 0 
        for room in self.rooms: 
            total += room.area
        return total 
    
class Room: 
    def __init__(self, area, name=None):
        self.area = area
        self.name = name
        self.devices = []

class SmartHouse:
    def __init__(self):
        self.floors = []
        self.devices = {}
    """
    This class serves as the main entity and entry point for the SmartHouse system app.
    Do not delete this class nor its predefined methods since other parts of the
    application may depend on it (you are free to add as many new methods as you like, though).

    The SmartHouse class provides functionality to register rooms and floors (i.e. changing the 
    house's physical layout) as well as register and modify smart devices and their state.
    """

    def register_floor(self, level):
        floor = Floor (level)
        self.floors.append(floor)
        return floor 
        """
        This method registers a new floor at the given level in the house
        and returns the respective floor object.
        """

    def register_room(self, floor, room_size, room_name = None):
        room = Room(room_size, room_name)
        floor.rooms.append(room)
        return room 
        """
        This methods registers a new room with the given room areal size 
        at the given floor. Optionally the room may be assigned a mnemonic name.
        """

    def get_floors(self):
        return sorted(self.floors, key=lambda f: f.level)
        """
        This method returns the list of registered floors in the house.
        The list is ordered by the floor levels, e.g. if the house has 
        registered a basement (level=0), a ground floor (level=1) and a first floor 
        (leve=1), then the resulting list contains these three flors in the above order.
        """

    def get_rooms(self):
        rooms = []
        for floor in self.floors:
            rooms.extend(floor.rooms)
        return rooms
        """
        This methods returns the list of all registered rooms in the house.
        The resulting list has no particular order.
        """


    def get_area(self):
        total = 0
        for room in self.get_room():
            total += room.area
        return total
        """
        This methods return the total area size of the house, i.e. the sum of the area sizes of each room in the house.
        """

    def register_device(self, room, device):
        room.devices.append(device)
        self.devices[device.device_id] = device
        """
        This methods registers a given device in a given room.
        """

    
    def get_device(self, device_id):
        return self.devices.get(device_id)
        """
        This method retrieves a device object via its id.
        """

