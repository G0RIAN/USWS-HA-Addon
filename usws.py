import random
import datetime

import hassapi as hass
from bs4 import BeautifulSoup
import urllib3


class USWS(hass.Hass):

    sensor_name = "sensor.usws"
    request_time_sec = random.Random.randint(0, 60)
    url = "https://lhg-902.iws.uni-stuttgart.de/"
    pool_manager = urllib3.PoolManager()

    # weather state attributes
    temp = None             # Air temperature
    temp_app = None         # Apparent air temperature
    precip_hourly = None    # Precipitation in the last hour
    precip_daily = None     # Precipitation daily sum
    press = None            # Air pressure MSL
    humid_rel = None        # Relative humidity
    vap_press = None        # Vapour pressure
    dew_pt = None           # Dew point
    rad_short_glob = None   # Global short-wave radiation
    rad_short_ref = None    # Reflected short-wave radiation
    rad_long_atm = None     # Atmospheric long-wave radiation
    rad_long_terr = None    # Terrestrial long-wave radiation
    wind_dir = None         # Wind direction
    wind_speed = None       # Wind speed
    wind_speed_sq = None    # Wind speed (squall)

    def initialize(self):
        self.request_time_sec = int(self.args.get("request_time_sec", self.request_time_sec))
        self.sensor_name = str(self.args.get("sensor_name", self.sensor_name))
        if self.sensor_name[0:7] != "sensor.":
            self.sensor_name = "sensor." + self.sensor_name
        self.run_minutely(self.run_minutely_callback, datetime.time(0, 0, self.request_time_sec))

    def terminate(self):
        pass

    def run_minutely_callback(self):
        response = self.pool_manager.request("GET", self.url)
        soup = BeautifulSoup(response.data())
        self.parse_weather_data(soup)
        self.update_entity()

    def parse_weather_data(self, soup):
        self.temp = float(soup.find("span", {"id": "T_c_1"}).text)
        self.temp_app = float(soup.find("span", {"id": "T_f_1"}).text)
        self.precip_hourly = float(soup.find("span", {"id": "N_1h_1"}).text)
        self.precip_daily = float(soup.find("span", {"id": "N_24h_d"}).text)
        self.press = float(soup.find("span", {"id": "P_c"}).text)
        self.humid_rel = int(soup.find("span", {"id": "rh_c_1"}).text)
        self.vap_press = float(soup.find("span", {"id": "ed_c"}).text)
        self.dew_pt = float(soup.find("span", {"id": "Td_c"}).text)
        self.rad_short_glob = float(soup.find("span", {"id": "G_c"}).text)
        self.rad_short_ref = float(soup.find("span", {"id": "RK_c"}).text)
        self.rad_long_atm = float(soup.find("span", {"id": "A_c"}).text)
        self.rad_long_terr = float(soup.find("span", {"id": "E_c"}).text)
        self.wind_dir = float(soup.find("span", {"id": "dd_c"}).text)
        self.wind_speed = 0.0  # TODO: get wind speed (maybe from image?)
        self.wind_speed_sq = float(soup.find("span", {"id": "u_cmax"}).text)

    def update_entity(self):
        attribs = {
            "temperature": self.temp,
            "apparent temperature": self.temp_app,
            "hourly precipitation": self.precip_hourly,
            "daily precipitation": self.precip_daily,
            "pressure": self.press,
            "humidity": self.humid_rel,
            "vapour pressure": self.vap_press,
            "dew point": self.dew_pt,
            "global short-wave radiation": self.rad_short_glob,
            "reflected short-wave radiation": self.rad_short_ref,
            "atmospheric long-wave radiation": self.rad_long_atm,
            "terrestrial long-wave radiation": self.rad_long_terr,
            "wind direction": self.wind_dir,
            "wind speed": self.wind_speed,
            "wind speed squall": self.wind_speed_sq
        }
        self.get_entity(self.sensor_name).set_state(self.temp, attribs)

