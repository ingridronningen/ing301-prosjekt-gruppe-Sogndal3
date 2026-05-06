import time
import requests

import logging
log_format = "%(asctime)s: %(message)s"
logging.basicConfig(format=log_format, level=logging.INFO, datefmt="%H:%M:%S")

import common

LIGHTBULB_CLIENT_SLEEP_TIME = 4

class ActuatorClient:
    """
    Actuator client representing the physical light bulb in the house
    using the cloud service to set is state
    """

    def __init__(self, did):
        self.did = did
        self.state = common.ActuatorState('off')

    def get_state(self) -> str:

        """
        This method sends a GET request to the cloud service to
        read/obtain the current state of the light bulb actuator.
        """

        logging.info(f"Actuator Client {self.did} retrieving state")
        actuator_state = None

        url = f"http://127.0.0.1:8000/smarthouse/actuator/{self.did}/state"
        
        try:
            response = requests.get(url)
            if response.status_code == 200:
                data = response.json()
                # Vi henter ut 'state' fra JSON-svaret
                # I common.py er ActuatorState ofte forventet som streng eller bool
                return data.get("state") 
            else:
                logging.error(f"Error retrieving state: {response.status_code}")
        except Exception as e:
            logging.error(f"Connection error: {e}")

        return None


    def run(self):
        """
        This method runs in a loop reguarly sending a request to the cloud service
        to set the current state of the light bulb in accordance with the state
        in the cloud service
        """
        logging.info(f"Actuator Client {self.did} starting loop")
        
        while True:
            # 1. Hent ny tilstand fra skyen
            new_state = self.get_state()
            
            if new_state is not None:
                # 2. Oppdater lokal tilstand (liksom-pæra endrer seg)
                self.state = new_state
                logging.info(f"Actuator {self.did} is now: {'ON' if self.state else 'OFF'}")
            
            # 3. Vent i noen sekunder før neste sjekk
            time.sleep(LIGHTBULB_CLIENT_SLEEP_TIME)


if __name__ == '__main__':

    actuator = ActuatorClient(common.LIGHT_BULB_ACTUATOR_DID)
    actuator.run()