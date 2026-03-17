import random
from datetime import datetime

class Measurement:
    def __init__(self, timestamp, value, unit):
        self.timestamp = timestamp
        self.value = value
        self.unit = unit

class Device:
    def __init__(self, id, supplier, model_name):
        self.id = id
        self.supplier = supplier
        self.model_name = model_name
        self.room = None
        self.device_type = "Device"

    def is_sensor(self):
        return False

    def is_actuator(self):
        return False

class Sensor(Device):
    def __init__(self, id, supplier, model_name, unit, sensor_type):
        super().__init__(id, supplier, model_name)
        self.unit = unit
        self.device_type = sensor_type

    def is_sensor(self):
        return True

    def last_measurement(self):
        value = round(random.uniform(0, 100), 2)
        timestamp = datetime.now().isoformat()
        return Measurement(timestamp, value, self.unit)

class Actuator(Device):
    def __init__(self, id, supplier, model_name, actuator_type):
        super().__init__(id, supplier, model_name)
        self.device_type = actuator_type
        self._active = False
        self.target_value = None

    def is_actuator(self):
        return True

    def turn_on(self, target_value=None):
        self._active = True
        if target_value is not None:
            self.target_value = target_value

    def turn_off(self):
        self._active = False
        self.target_value = None

    def is_active(self):
        return self._active


class Floor:
    def __init__(self, level):
        self.level = level
        self.rooms = []

    def get_area(self):
        return sum(room.area for room in self.rooms)


class Room:
    def __init__(self, area, room_name=None):
        self.area = area
        self.room_name = room_name
        self.devices = []

class SmartHouse:
    def __init__(self):
        self.floors = []
        self.devices = {}

    def register_floor(self, level):
        floor = Floor(level)
        self.floors.append(floor)
        return floor

    def register_room(self, floor, room_size, room_name=None):
        room = Room(room_size, room_name)
        floor.rooms.append(room)
        return room

    def get_floors(self):
        return sorted(self.floors, key=lambda f: f.level)

    def get_rooms(self):
        rooms = []
        for floor in self.floors:
            rooms.extend(floor.rooms)
        return rooms

    def get_area(self):
        return sum(room.area for room in self.get_rooms())

    def register_device(self, room, device):
        if device.room is not None:
            device.room.devices.remove(device)
        room.devices.append(device)
        device.room = room
        self.devices[device.id] = device

    def get_devices(self):
        return list(self.devices.values())

    def get_device_by_id(self, id):
        return self.devices.get(id, None)