import common
import requests

class SmartHouseApp:
    def __init__(self):
        self.sensor_did = common.TEMPERATURE_SENSOR_DID
        self.actuator_did = common.LIGHT_BULB_ACTUATOR_DID

    def get_bulb_state(self) -> str:
        """ Henter status og returnerer 'on' eller 'off' for å matche main-logikken """
        url = common.BASE_URL + f"actuator/{self.actuator_did}/state"
        try:
            response = requests.get(url)
            if response.status_code == 200:
                actuator_state = common.ActuatorState.from_json_str(response.text)
                # Oversetter True -> 'on' og False -> 'off'
                return "on" if actuator_state.state else "off"
        except Exception as e:
            print(f"Error getting bulb state: {e}")
        return "off"

    def update_bulb_state(self, new_state_str) -> requests.Response:
        """ Tar inn 'on' eller 'off', og sender True eller False til skyen """
        url = common.BASE_URL + f"actuator/{self.actuator_did}/state"
        
        # Oversetter tekst tilbake til bool før sending
        bool_state = True if new_state_str == "on" else False
        
        payload = {"state": bool_state}
        response = requests.put(url, json=payload)
        return response

    def get_temperature(self) -> float:
        """ Henter temperaturmåling fra skyen """
        url = common.BASE_URL + f"sensor/{self.sensor_did}/current"
        try:
            response = requests.get(url)
            if response.status_code == 200:
                measurement = common.SensorMeasurement.from_json_str(response.text)
                return measurement.value
        except Exception as e:
            print(f"Error getting temperature: {e}")
        return 0.0

    def main(self):
        is_active = True

        while is_active:
            print("\n---- SmartHouse Control App ----\nSelect option:\n1. Toggle Lightbulb \n2. Show Temperature\n3. Quit\n")
            user_input = input(">>> ")

            # Sjekker om input faktisk er et av de gyldige tallene
            if user_input.isdigit() and int(user_input) in {1, 2, 3}:
                selected_option = int(user_input)
                
                if selected_option == 1:
                    # 1. Hent nåværende (får f.eks. 'off')
                    current_state = self.get_bulb_state()
                    print(f'Current state lightbulb: {current_state}')

                    # 2. Bytt til motsatt tekst
                    target_state = 'on' if current_state == 'off' else 'off'

                    # 3. Send oppdatering
                    self.update_bulb_state(target_state)
                    
                    # 4. Bekreft endring
                    new_state = self.get_bulb_state()
                    print(f'New state lightbulb: {new_state}')

                elif selected_option == 2:
                    value = self.get_temperature()
                    print(f'Current temperature: {value}')

                elif selected_option == 3:
                    is_active = False
            else:
                print(f"Unrecognized input: '{user_input}'")

        print("App shutting down")

if __name__ == '__main__':
    app = SmartHouseApp()
    app.main()