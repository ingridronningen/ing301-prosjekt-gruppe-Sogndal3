import uvicorn

import logging
from fastapi import FastAPI, Response
from fastapi.staticfiles import StaticFiles
from fastapi.responses import RedirectResponse, JSONResponse
from fastapi.encoders import jsonable_encoder

from tests.demo_house import DEMO_HOUSE

from smarthouse.domain import Actuator, Measurement
from smarthouse.dto import SmartHouseInfo, FloorInfo, RoomInfo, DeviceInfo, ActuatorStateInfo

from pathlib import Path
import os
app = FastAPI()

smarthouse = DEMO_HOUSE

if not (Path.cwd() / "www").exists():
    os.chdir(Path.cwd().parent)
if (Path.cwd() / "www").exists():
    # http://localhost:8000/welcome/index.html
    app.mount("/static", StaticFiles(directory="www"), name="static")

# http://localhost:8000/ -> welcome page
@app.get("/")
def root():
    return RedirectResponse("/static/index.html")

# Health Check / Hello World
@app.get("/hello")
def hello(name: str = "world"):
    return {"hello": name}

#
# API endpoints for the smarthouse structural resources
#

@app.get("/smarthouse")
def get_smarthouse_info() -> SmartHouseInfo:
    """
    This endpoint returns an object that provides information
    about the general structure of the smarthouse.
    """
    return SmartHouseInfo.from_obj(smarthouse)


@app.get("/smarthouse/floor")
def get_floors() -> list[FloorInfo]:
    return [FloorInfo.from_obj(x) for x in smarthouse.get_floors()]

@app.get("/smarthouse/floor/{fid}")
def get_floor(fid: int) -> Response:
    for f in smarthouse.get_floors():
        if f.level == fid:
            return JSONResponse(content=jsonable_encoder(FloorInfo.from_obj(f)))
    return Response(status_code=404)

@app.get("/smarthouse/floor/{fid}/room")
def get_rooms(fid: int) -> list[RoomInfo]:
    for f in smarthouse.get_floors():
        if f.level == fid:
            # Bruker RoomInfo.from_obj for å konvertere hvert rom
            return [RoomInfo.from_obj(r) for r in f.rooms]
    return []

@app.get("/smarthouse/floor/{fid}/room/{rid}")
def get_room(fid: int, rid: int) -> Response:
    for f in smarthouse.get_floors():
        if f.level == fid:
            for r in f.rooms:
                # Sjekk om rom-id (rid) matcher. Merk: sjekk hva variabelnavnet for ID er i din Room-klasse
                if r.rid == rid: 
                    return JSONResponse(content=jsonable_encoder(RoomInfo.from_obj(r)))
    return Response(status_code=404)    

@app.get("/smarthouse/device")
def get_devices() -> list[DeviceInfo]:
    devices = smarthouse.get_devices()
    return [DeviceInfo.from_obj(d) for d in devices]

@app.get("/smarthouse/device/{uuid}")
def get_device(uuid: str) -> Response:
    device = smarthouse.get_device_by_id(uuid)
    if device:
        # Vi bruker jsonable_encoder for å gjøre Pydantic-objektet klart for JSONResponse
        return JSONResponse(content=jsonable_encoder(DeviceInfo.from_obj(device)))
    
    # Returnerer 404 hvis enheten ikke finnes
    return Response(status_code=404)

#
# API endpoints for sensors resources
#

@app.get("/smarthouse/sensor/{uuid}/current")
def read_measurement(uuid: str) -> Response:
    device = smarthouse.get_device_by_id(uuid)

    # Sjekk om enheten i det hele tatt finnes
    if not device:
        return Response(status_code=404, content="Device not found")

    # Sjekk om det faktisk er en sensor
    if not device.is_sensor():
        return Response(status_code=400, content="Device is not a sensor")

    measurement = device.get_current()
    
    if measurement:
        return JSONResponse(content=jsonable_encoder(measurement))
    
    # Hvis sensoren finnes, men er tom, returnerer vi 204 No Content
    # Dette er ofte det Bruno-tester forventer hvis de ikke har "puttet" data ennå
    return Response(status_code=204)

@app.put("/smarthouse/sensor/{uuid}/current")
def update_sensor_measurement(uuid: str, measurement: Measurement) -> Response:
    # 1. Finn enheten i huset
    device = smarthouse.get_device_by_id(uuid)
    
    # 2. Sjekk om den finnes og faktisk er en sensor
    if device and device.is_sensor():
        # 3. Bruk metoden fra domain.py til å lagre målingen
        device.set_current(measurement)
        return Response(status_code=200)
    
    # Hvis enheten ikke finnes eller ikke er en sensor
    return Response(status_code=404)

@app.delete("/smarthouse/sensor/{uuid}/current")
def delete_measurement(uuid: str) -> Response:
    device = smarthouse.get_device_by_id(uuid)
    if device and device.is_sensor():
        device.current = None  # Sletter den nåværende målingen
        return Response(status_code=200)
    return Response(status_code=404)

#
# API endpoints for actuator resources
#

@app.get("/smarthouse/actuator/{uuid}/state")
def read_actuator_state(uuid: str) -> Response:
    device = smarthouse.get_device_by_id(uuid)
    
    # Sjekk om device finnes og om den faktisk har en 'is_actuator' metode som returnerer True
    if device and device.is_actuator():
        # Vi må kaste den til en Actuator-type (logisk sett) for at DTO skal fungere
        state_dto = ActuatorStateInfo.from_obj(device)
        return JSONResponse(content=jsonable_encoder(state_dto))
    
    return Response(status_code=404)

@app.put("/smarthouse/actuator/{uuid}/state")
def update_sensor_state(uuid: str, target_state: ActuatorStateInfo) -> Response:
    # 1. Finn enheten
    device = smarthouse.get_device_by_id(uuid)
    
    if device and device.is_actuator():
        # Siden klassen din bruker 'self.state', må vi oppdatere den her:
        device.state = target_state.state 
        
        # Logg for å bekrefte i terminalen
        print(f"DEBUG: Satte device.state til {device.state}")
        
        return Response(status_code=200)
    
    return Response(status_code=404)

if __name__ == '__main__':
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8000) 

