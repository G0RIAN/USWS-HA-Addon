import random
import datetime

import hassapi as hass
from bs4 import BeautifulSoup
import urllib3


class USWS(hass.Hass):

    sensor_name = "sensor.usws"
    request_time_sec = random.Random().randint(0, 59)
    url = "https://lhg-902.iws.uni-stuttgart.de/"
    pool_manager = urllib3.PoolManager()

    sensor_data = dict()

    def initialize(self):
        self.request_time_sec = int(self.args.get("request_time_sec", self.request_time_sec))
        self.sensor_name = str(self.args.get("sensor_name", self.sensor_name))
        if self.sensor_name[0:7] != "sensor.":
            self.sensor_name = "sensor." + self.sensor_name
        self.run_minutely(self.run_minutely_callback, datetime.time(0, 0, self.request_time_sec))

    def terminate(self):
        pass

    def run_minutely_callback(self, kwargs):
        response = self.pool_manager.request("GET", self.url)
        soup = BeautifulSoup(response.data)
        self.parse_weather_data(soup)
        self.update_entity()

    def parse_weather_data(self, soup):
        self.sensor_data = dict()
        span_ids = {
           "temperature": "T_c_1",
           "apparent temperature": "T_f_1",
           "hourly precipitation": "N_1h_1",
           "daily precipitation": "N_24h_d",
           "pressure": "P_c",
           "humidity": "rh_c_1",
           "vapour pressure": "ed_c",
           "dew point": "Td_c",
           "global short-wave radiation": "G_c",
           "reflected short-wave radiation": "RK_c",
           "atmospheric long-wave radiation": "A_c",
           "terrestrial long-wave radiation": "E_c",
           "wind direction": "dd_c",
           #  "wind speed": "???",
           "wind speed squall": "u_cmax"
        }

        for key, span_id in span_ids:
            try:
                result = soup.find("span", {"id": span_id})
                if result is not None:
                    self.sensor_data[key] = float(result.text)
            except Exception as e:
                print(e)


        self.sensor_data["wind speed"] = 0.0  # TODO: get wind speed (maybe from image?)

    def update_entity(self):
        attribs = self.sensor_data
        attribs.pop("temperature")
        self.get_entity(self.sensor_name).set_state(self.sensor_data["temperature"], attribs)

