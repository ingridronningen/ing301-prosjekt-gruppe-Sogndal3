import sqlite3
from typing import Optional
from smarthouse.domain import Measurement, SmartHouse, Room, Floor, Sensor, Actuator

class SmartHouseRepository:
    """
    Provides the functionality to persist and load a _SmartHouse_ object 
    in a SQLite database.
    """

    def __init__(self, file: str) -> None:
        self.file = file 
        self.conn = sqlite3.connect(file, check_same_thread=False)

    def __del__(self):
        self.conn.close()

    def cursor(self) -> sqlite3.Cursor:
        """
        Provides a _raw_ SQLite cursor to interact with the database.
        When calling this method to obtain a cursors, you have to 
        rememeber calling `commit/rollback` and `close` yourself when
        you are done with issuing SQL commands.
        """
        return self.conn.cursor()

    def reconnect(self):
        self.conn.close()
        self.conn = sqlite3.connect(self.file)

    
    def load_smarthouse_deep(self):
        """
        This method retrives the complete single instance of the _SmartHouse_ 
        object stored in this database. The retrieval yields a _deep_ copy, i.e.
        all referenced objects within the object structure (e.g. floors, rooms, devices) 
        are retrieved as well. 
        """
        # TODO: START here! remove the following stub implementation and implement this function 
        #       by retrieving the data from the database via SQL `SELECT` statements.
        # (henter alle rom og devices, koble devices til rom og bygge et SmartHouse-objekt)
        cursor = self.cursor()

        cursor.execute ("SELECT id, floor, area, name FROM rooms")  # henter rom
        rooms_data = cursor.fetchall()

        cursor.execute ("SELECT id, room, kind, category, supplier, product, state FROM devices")  # henter devices
        devices_data = cursor.fetchall()

        cursor.close()

        house = SmartHouse()

        room_map = {}    # floor + room kobling 
        floors_map = {}
        for r_id, floor_level, area, room_name in rooms_data:
            if floor_level not in floors_map:
                floor = Floor(floor_level)
                floors_map[floor_level] = floor
                house.floors.append(floor)
            else:
                floor = floors_map[floor_level]

            room = Room(area, room_name)
            floor.rooms.append(room)
            room_map[r_id] = room

        # Opprett devices og koble til rom
        for d_id, room_id, kind, category, supplier, product, state in devices_data:
            room = room_map.get(room_id)

            if kind.lower() == "sensor":
                device = Sensor(d_id, supplier, product, unit="unknown", sensor_type=category)
            else:
                device = Actuator(d_id, supplier, product, actuator_type=category)
                if state == 1:
                    device.turn_on()
                else:
                    device.turn_off()

            if room:    #legger device inn i rom 
                room.devices.append(device)

            house.devices[d_id] = device
        
        return house

    def get_latest_reading(self, sensor) -> Optional[Measurement]:
        """
        Retrieves the most recent sensor reading for the given sensor if available.
        Returns None if the given object has no sensor readings.
        """
        # TODO: After loading the smarthouse, continue here
        #(henter siste måling fra measurments for en sensor)

        cursor = self.cursor()
        cursor.execute(
            """SELECT ts, value, unit 
            FROM measurements 
            WHERE device = ? 
            ORDER BY ts DESC 
            LIMIT 1""",
            (sensor.id,)
        )
        row = cursor.fetchone()
        cursor.close()

        if row:
            return Measurement(timestamp=row[0], value=row[1], unit=row[2])
        return None

    def update_actuator_state(self, actuator):
        """
        Saves the state of the given actuator in the database. 
        """
        # TODO: Implement this method. You will probably need to extend the existing database structure: e.g.
        #       by creating a new table (`CREATE`), adding some data to it (`INSERT`) first, and then issue
        #       and SQL `UPDATE` statement. Remember also that you will have to call `commit()` on the `Connection`
        #       stored in the `self.conn` instance variable.
   
        cursor = self.cursor()
        cursor.execute(
            """UPDATE devices
               SET state = ?
               WHERE id = ?""",
            (1 if actuator.is_active() else 0, actuator.id)
        )
        self.conn.commit()
        cursor.close()

    # statistics

    
    def calc_avg_temperatures_in_room(self, room, from_date: Optional[str] = None, until_date: Optional[str] = None) -> dict:
        """Calculates the average temperatures in the given room for the given time range by
        fetching all available temperature sensor data (either from a dedicated temperature sensor 
        or from an actuator, which includes a temperature sensor like a heat pump) from the devices 
        located in that room, filtering the measurement by given time range.
        The latter is provided by two strings, each containing a date in the ISO 8601 format.
        If one argument is empty, it means that the upper and/or lower bound of the time range are unbounded.
        The result should be a dictionary where the keys are strings representing dates (iso format) and 
        the values are floating point numbers containing the average temperature that day.
        """
        # TODO: This and the following statistic method are a bit more challenging. Try to design the respective 
        #       SQL statements first in a SQL editor like Dbeaver and then copy it over here.  
        #(SQL-spørring som henter temp målinger for et rom og regner gjennomsnitt per dag)
        
        cursor = self.cursor()

        # Hent alle sensorer i rommet som har temperatur-data:
        device_ids = [d.id for d in room.devices]
        if not device_ids:
            return {}

        # Lag SQL IN-list
        placeholders = ",".join("?" for _ in device_ids)

        sql = f"""
            SELECT DATE(ts) as day, AVG(value)
            FROM measurements
            WHERE device IN ({placeholders})
            AND unit = '°C'
        """
        params = list(device_ids)

        # Legg til tidsbegrensning hvis gitt
        if from_date:
            sql += " AND DATE(ts) >= ?"
            params.append(from_date)

        if until_date:
            sql += " AND DATE(ts) <= ?"
            params.append(until_date)

        sql += " GROUP BY DATE(ts) ORDER BY DATE(ts)"

        cursor.execute(sql, params)
        rows = cursor.fetchall()
        cursor.close()

        # Lag dict med {dato: gjennomsnitt}
        return {row[0]: row[1] for row in rows}

    
    def calc_hours_with_humidity_above(self, room, date: str) -> list:
        """
        This function determines during which hours of the given day
        there were more than three measurements in that hour having a humidity measurement that is above
        the average recorded humidity in that room at that particular time.
        The result is a (possibly empty) list of number representing hours [0-23].
        """
        # TODO: implement
        #(SQL-spørring som teller timer med >3 målinger over gjennomsnitt)

        cursor = self.cursor()

        # Hent alle humidity-sensorer i rommet
        device_ids = [d.id for d in room.devices]
        if not device_ids:
            return []

        placeholders = ",".join("?" for _ in device_ids)

        # 1. Finn gjennomsnittet for hele dagen i det rommet for enheter med '%'
        cursor.execute(
            f"SELECT AVG(value) FROM measurements WHERE device IN ({placeholders}) AND DATE(ts) = ? AND unit = '%'",
            device_ids + [date]
        )
        avg_row = cursor.fetchone()
        if not avg_row or avg_row[0] is None:
            return []
        
        day_avg = avg_row[0]

        # 2. Finn timer som har MER enn 3 målinger som er høyere enn dette dagsgjennomsnittet
        # "more than three" betyr > 3 (altså 4 eller flere)
        sql = f"""
            SELECT STRFTIME('%H', ts) as hour
            FROM measurements
            WHERE device IN ({placeholders}) 
              AND DATE(ts) = ? 
              AND unit = '%'
              AND value > ?
            GROUP BY hour
            HAVING COUNT(*) > 3
            ORDER BY hour
        """
        
        cursor.execute(sql, device_ids + [date, day_avg])
        rows = cursor.fetchall()
        cursor.close()

        return [int(row[0]) for row in rows]