import random
import datetime
import numpy as np
import re
import io

from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
import urllib.request
import cv2
from PIL import Image
import pytesseract

from hassapi import Hass


class USWS(Hass):

    sensor_name = "sensor.usws"
    request_time_sec = random.Random().randint(0, 59)
    url = "https://lhg-902.iws.uni-stuttgart.de/"
    driver = None
    sensor_data = dict()

    def initialize(self):
        chrome_options = Options()
        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument("--headless")
        chrome_options.add_argument("--start-maximized")
        chrome_options.add_argument('--disable-gpu')
        chrome_options.add_argument('--disable-dev-shm-usage')
        chrome_options.add_argument("--window-size=1920,1080")
        chrome_options.add_argument("--ignore-certificate-errors")
        self.driver = webdriver.Chrome("chromedriver", options=chrome_options)

        self.request_time_sec = int(self.args.get("request_time_sec", self.request_time_sec))
        self.sensor_name = str(self.args.get("sensor_name", self.sensor_name))
        if self.sensor_name[0:7] != "sensor.":
            self.sensor_name = "sensor." + self.sensor_name
        self.run_minutely(self.run_minutely_callback, datetime.time(0, 0, self.request_time_sec))

    def terminate(self):
        pass

    def run_minutely_callback(self, *args, **kwargs):
        self.driver.get(self.url)
        soup = BeautifulSoup(self.driver.page_source, "html.parser")
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
            "wind speed squall": "u_cmax"
        }

        for key, span_id in span_ids.items():
            try:
                result = soup.find("span", {"id": span_id})
                if result is not None:
                    self.sensor_data[key] = float(result.text)
            except Exception as e:
                print(e)

        # get wind speed from image OCR
        try:
            # prepare image
            wind_speed_url = soup.find("img", {"id": "wr_light_container"})['src']
            with urllib.request.urlopen(self.url + wind_speed_url[1:]) as url:
                resp = url.read()
                tmp_img = io.BytesIO(resp)
                img_open = Image.open(tmp_img)
                img = np.asarray(img_open, dtype="uint8")[:, :, :-1]

            # rotate image
            image_center = tuple(np.array(img.shape[1::-1]) / 2)
            rot_mat = cv2.getRotationMatrix2D(image_center, self.sensor_data["wind direction"] - 90, 1.0)
            img_rot = cv2.warpAffine(img, rot_mat, img.shape[1::-1], flags=cv2.INTER_LINEAR)
            cv2.imwrite("./test_rot.png", img_rot)

            # crop image
            cv2.imwrite("./test_rot_crop.png", img_rot[135:165, 80:220])

            # use OCR to read wind speed
            config = ('-l eng --oem 1 --psm 3')
            text = pytesseract.image_to_string(img_rot[135:165, 80:220], config=config)
            print(text)
            re_matches = re.findall(r"\d?\d.\d", text)
            if len(re_matches) == 1:
                self.sensor_data["wind speed"] = float(re_matches[0])
            elif len(re_matches) > 1:
                print("Found more than 1 matching text string in image!")
            else:
                print("No text found")

        except Exception as e:
            self.sensor_data["wind speed"] = 0.0
            print(e)

    def update_entity(self):
        attribs = self.sensor_data
        attribs["device_class"] = "temperature"
        attribs["state_class"] = "measurement"
        attribs["unit_of_measurement"] = "°C"
        attribs["friendly_name"] = "Uni Stuttgart Weather Sensor (USWS)"
        self.set_state(self.sensor_name, state=attribs.pop("temperature", "unknown"), attributes=attribs)
