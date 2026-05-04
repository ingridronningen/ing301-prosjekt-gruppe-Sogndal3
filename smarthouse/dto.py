from __future__ import annotations
from typing import Literal, Union, Optional, List

from pydantic import BaseModel
from smarthouse.domain import Actuator, ActuatorWithSensor, Device, Floor, Room, Sensor, SmartHouse

"""
Classes for data transfer in the cloud service API endpoints between
what is sent/received int eh API and the data stored in the object structure
representing the smart house using the underlying domain model
"""

class SmartHouseInfo(BaseModel):

    no_rooms: int
    no_floors: int
    total_area: float
    no_devices: int

    @staticmethod
    def from_obj(house: SmartHouse) -> SmartHouseInfo:
        return SmartHouseInfo(
            no_rooms=len(house.get_rooms()),
            no_floors=len(house.get_floors()),
            total_area=house.get_area(),
            no_devices=len(house.get_devices()))


class FloorInfo(BaseModel):

    fid: int
    rooms: list[int]

    @staticmethod
    def from_obj(floor: Floor) -> FloorInfo:
        return FloorInfo(
            fid=floor.level,
            rooms=[r.rid for r in floor.rooms]
        )

class RoomInfo(BaseModel):

    rid: int | None
    room_size: float
    room_name: str | None
    floor: int
    devices: list[str]

    @staticmethod
    def from_obj(room: Room) -> RoomInfo:
        return RoomInfo(
            rid=room.rid,
            room_size=room.room_size,
            room_name=room.room_name,
            floor=room.floor.level,
            devices=[d.id for d in room.devices] 
        )

class DeviceInfo(BaseModel):
    uuid: str
    name: str
    type: str 
    room: int | None

    @staticmethod
    def from_obj(device: Device) -> DeviceInfo:
        # Bestemmer type-strengen basert på klassen
        if isinstance(device, ActuatorWithSensor):
            d_type = "both"
        elif isinstance(device, Sensor):
            d_type = "sensor"
        elif isinstance(device, Actuator):
            d_type = "actuator"
        else:
            d_type = "unknown"

        return DeviceInfo(
            uuid=device.id,
            name=device.model_name,
            type=d_type,
            room=device.room.rid if device.room else None
        )

class ActuatorStateInfo(BaseModel):
    state: Union[float, bool]

    @staticmethod
    class ActuatorStateInfo(BaseModel):
        state: Union[bool, float]

    @classmethod
    def from_obj(cls, obj):
    # Hvis denne linjen henter feil variabel, vil appen alltid tro den er OFF
    # Siden du har en is_active() metode i domain.py, bør vi bruke den:
        return cls(state=obj.is_active())
 
ActuatorStateInfo.model_rebuild()