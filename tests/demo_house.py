from smarthouse.domain import SmartHouse

DEMO_HOUSE = SmartHouse()

# Building house structure
ground_floor = DEMO_HOUSE.register_floor(1)
entrance = DEMO_HOUSE.register_room(ground_floor, 13.5, "Entrance")
# TODO: continue registering the remaining floor, rooms and devices


DEMO_HOUSE.register_device(entrance, Smart_lock)
DEMO_HOUSE.register_device(entrance, Electricity_meter)
DEMO_HOUSE.register_device(living_room, CO2_sensor)
DEMO_HOUSE.register_device(living_room, Heat_Pump)
DEMO_HOUSE.register_device(living_room, Motion_sensor)
DEMO_HOUSE.register_device(Bathroom1, Humidity_sensor)
DEMO_HOUSE.register_device(Guest_Room1, Smart_Oven1)
DEMO_HOUSE.register_device(Garage, Automativc_Garage_Door)
DEMO_HOUSE.register_device(Office, Smart_Plug)
DEMO_HOUSE.register_device(Bathroom2, Dehumidifyer)
DEMO_HOUSE.register_device(Guest_Room2, Light_Bulb)
DEMO_HOUSE.register_device(Guest_Room3, Air_Quality_Sensor)
DEMO_HOUSE.register_device(Master_Bedroom, Temperature_Sensor)
DEMO_HOUSE.register_device(Master_Bedroom, Smart_Oven)