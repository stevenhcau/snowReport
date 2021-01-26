#!/usr/bin/env python3

# Requests is used to access api
# JSON is used to parse API response from JSON format into a list of dictionaries
# os is used to set current directory and folder structure
# dateutil.parser as dp is used to convert UTC format into datetime format
# datetime and tzlocal is used to convert UTC timezone into Canada/Mountain Time

import json
import os
from datetime import datetime
import dateutil.parser as dp
import logging
import sys
import requests
from tzlocal import get_localzone

"""
This program:
    - retrieves weather API information from several sources
    - gathers weather data for popular ski resorts
    - displays ski resorts that are expecting significant snowfall in a 7 day forecast

    The program will have three functions:
        - Realtime weather checking and short term forecasting (360 minutes out)
        - Forecast for snow in 96 hour forecast

Realtime weather and shorterm forecast:
    - Display current weather conditions
    - Display short term weather forecast

96 hour forecast:
    - The program should request for which resorts to monitor.
    - It will then check the 96 hour forecast to see if there is snow.
    - If there is snow, the program should notify the end user and then display the forecast. 

Using climacell API for weather data. API key: G6pKgE1QNQqjkSM5XzBZMW5N7cPgxUVy
skiResort data is stored in skiResorts.json
"""

# GLOBAL VARS
URL_HOURLY = "https://api.climacell.co/v3/weather/forecast/hourly"
URL_NOWCAST = "https://api.climacell.co/v3/weather/nowcast"
URL_REALTIME = "https://api.climacell.co/v3/weather/realtime"
SKI_RESORT_JSON = "skiResorts.json"
CLIMACELL_KEY = "G6pKgE1QNQqjkSM5XzBZMW5N7cPgxUVy"

STARRED_RESORTS = ["lakeLouise", "sunshine", "fernie", "revelstoke", "whistler"]
ALBERTA_RESORTS = ["lakeLouise", "sunshine", "nakiska", "castleMountain", "norquay"]


# Sets up where the files will be
ABS_PATH = os.path.abspath(__file__)
D_NAME = os.path.dirname(ABS_PATH)
currentDir = os.getcwd()

if currentDir != D_NAME:
    os.chdir(D_NAME)
else:
    pass

# Set up logging at the debug level
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)
handler = logging.FileHandler(filename='snowApp.log', encoding='utf-8', mode='w')
handler.setFormatter(logging.Formatter('%(asctime)s:%(levelname)s:%(name)s: %(message)s'))
logger.addHandler(handler)

logger.debug(f'Running snowReport.py... \n')

logger.debug(f'ABS_PATH: {ABS_PATH}')
logger.debug(f'D_NAME: {D_NAME}')
logger.debug(f'Current Directory: {currentDir} \n')

# This method takes the string of a time in ISO 8601 format and converts it to local time using the system timezone
def local_time(UTC_time):
    return dp.parse(UTC_time).astimezone(
        get_localzone()
    )  # returns a datetime.datetime object


# This method adds a resort to the json file, returns the skiResort json file
def add_new_resort(resort_key, resort_name, country, lat, lon):
    logger.debug(f'Function call: add_new_resort()')
    logger.debug(f'Adding new resort: {resort_name}')

    new_resort_dict = {
        resort_key: {"name": resort_name, "country": country, "lat": lat, "lon": lon}
    }

    with open(SKI_RESORT_JSON, "r") as f:
        resort_json = json.load(f)
        if resort_key in resort_json:
            logger.debug(f'{resort_key} already exists in the json file, failure to add new resort')
            logger.debug(f'Please change the resort key name and try again \n')
        else:
            resort_json.update(new_resort_dict)

            with open(SKI_RESORT_JSON, "w") as f:
                json.dump(resort_json, f, indent=4)
                logger.debug(f"Added {resort_name} successfully \n")

    return resort_json

# This method lists the set of resort keys and the corresponding resort name that the user can access
def get_resort_keys():
    logger.debug('Function call: get_resort_keys() \n')
    current_dir = os.getcwd()
    logger.debug('The current directory: {current_dir}')

    if current_dir != D_NAME:
        os.chdir(D_NAME)
        logger.debug('Current directory was not as expected.')
        logger.debug('The current directory was set to: {D_NAME}')
    else:
        pass

    # Opens json file to get location parameters
    with open(SKI_RESORT_JSON, "r") as f:
        ski_resort_dict = json.load(f)

    ski_resort_keys = ski_resort_dict.keys()
    ski_resort_names = [ski_resort_dict[resort_key]['name'] for resort_key in ski_resort_keys]
    resort_keys = {ski_resort_names[i]: ski_resort_keys[i] for i in range(len(ski_resort_names))}

    return resort_keys

    

# Get request modified to only pull the data requested by the user using args
# Question: are kwargs or args better to use in this situation?
# Defines a class "Resort" to handle the attributes and methods for each ski resort
# Init function creates a new instance of your class
# Init function should only initiate your variable
# Lines 105 to 108, good to instantiate in the init
# self.args = args
# create a new function that is called process request
# request item in self.args
class Resort():
    # kwargs is created so the user can pass in "96hr", "realtime", and or "360min"
    def __init__(self, resort_key):
        logger.debug('Creating new instance of Resort Class. Resort key: {resort_key}')
        # Check if you are in the current directory, if not, set it to the current directory
        
        current_dir = os.getcwd()
        logger.debug('The current directory: {current_dir}')

        if current_dir != D_NAME:
            os.chdir(D_NAME)
            logger.debug('Current directory was not as expected.')
            logger.debug('The current directory was set to: {D_NAME}')
        else:
            pass

        # Opens json file to get location parameters
        with open(SKI_RESORT_JSON, "r") as f:
            resort_dict_list = json.load(f)
            resort_dict = resort_dict_list[resort_key]

        self.name = resort_dict["name"]
        self.lon = resort_dict["lon"]
        self.lat = resort_dict["lat"]
        self.country = resort_dict["country"]

        self.weather_now = {}
        self.weather_6hr = {}
        self.weather_96hr = {}

        logger.debug('New "Resort" object successfully initialized... \n')

    # Makes a request to the API to retrieve a dictionary containing the current weather
    def request_now(self):
        logger.debug(f'Function call: request_now()')
        querystring = {
            "lat": str(self.lat),
            "lon": str(self.lon),
            "unit_system": "si",
            "fields": "precipitation,precipitation_type,temp,feels_like,wind_speed,wind_direction,sunrise,sunset,visibility,cloud_cover,cloud_base,weather_code",
            "apikey": CLIMACELL_KEY,
        }

        response = requests.request("GET", URL_REALTIME, params=querystring)

        if response.ok:
            logger.debug(f'request_now() to Climacell API successful \n')
            self.weather_now = json.loads(response.text)

            self.now_time = local_time(self.weather_now["observation_time"]["value"])
            self.now_temperature = self.weather_now["temp"]["value"]
            self.now_feelslike = self.weather_now["feels_like"]["value"]
            self.now_precipitation = self.weather_now["precipitation"]["value"]
            self.now_precipitation_type = self.weather_now["precipitation_type"]["value"]
            self.now_windspeed = self.weather_now["wind_speed"]["value"]
            self.now_winddirection = self.weather_now["wind_direction"]["value"]
            self.now_cloudcover = self.weather_now["cloud_cover"]["value"]

            return True  

        else:
            logger.debug(f'request_now() to Climacell API failed \n')                
            return False

    # Makes a request to the API to retrieve a dictionary containing 6hr weather, returns True if successful, returns False if call wasn't successful
    def request_6hr(self):
        logger.debug(f'Function call: request_6hr')
        querystring = {
            "lat": str(self.lat),
            "lon": str(self.lon),
            "unit_system": "si",
            "timestep": "5",
            "start_time": "now",
            "fields": "temp,feels_like,humidity,wind_speed,wind_direction,precipitation,precipitation_type,sunrise,sunset,visibility,cloud_cover,cloud_base,weather_code",
            "apikey": CLIMACELL_KEY,
        }

        response = requests.request("GET", URL_NOWCAST, params=querystring)

        if response.ok:
            logger.debug(f'request_6hr()  to Climacell API successful \n')            
            self.weather_6hr = json.loads(response.text)
            return True

        else:
            logger.debug(f'request_6hr() to Climacell API failed \n')              
            return False

    # Makes a request to the API to retrieve a dictonary containing 96hr weather, returns True if successful, returns False if call wasn't successful
    def request_96hr(self):
        logger.debug(f'Function call: request_96hr()')
        querystring = {
            "lat": str(self.lat),
            "lon": str(self.lon),
            "unit_system": "si",
            "start_time": "now",
            "fields": "precipitation,temp,feels_like,humidity,wind_speed,wind_direction,precipitation_type,precipitation_probability,sunrise,sunset,cloud_cover,cloud_base,weather_code",
            "apikey": CLIMACELL_KEY,
        }
        response = requests.request("GET", URL_HOURLY, params=querystring)  # ClimaCell: The hourly call provides a global hourly forecast, up to 96 hours (4 days) out, for a specific location.
        if response.ok:
            logger.debug(f'request_96hr() to Climacell API successful \n')  
            self.weather_96hr = json.loads(response.text)
            return True
        else:
            logger.debug(f'request_96hr() to Climacell API failed \n')  
            return False

    # Class method to process requests
    def process_requests(self):
        logger.debug(f'Function call: process_requests()')
        # Makes a request for realtime data and stores in self.weather_now
        self.request_now()
        # Makes a request for 6hr forecast and stores in self.weather_6hr
        self.request_6hr()
        # Makes a request for 96hr forecast and stores in self.weather_96hr
        self.request_96hr() 
        logger.debug(f'Completed function call... process_requests()')

# Temperature

    # Class method get_temperature_96hr() returns a dictionary of the temperature against time
    def get_temperature_96hr(self):
        logger.debug(f'Function call: get_temperature_96hr()')
        time_96hr = [local_time(self.weather_96hr[i]["observation_time"]["value"]) for i in range(0, len(self.weather_96hr))]
        temp_96hr = [self.weather_96hr[i]["temp"]["value"] for i in range(0, len(self.weather_96hr))]
        self.temperature_forecast_96hr = {time_96hr[i]: temp_96hr[i] for i in range(len(time_96hr))}
        logger.debug(f'Returning dictionary containing time:value pair, "self.temperature_forecast_96hr \n')
        return self.temperature_forecast_96hr

    # Class method get_temperature_6hr() returns a dictionary of the temperature against time
    def get_temperature_6hr(self):
        logger.debug(f'Function call: get_temperature_6hr()')
        time_6hr = [local_time(self.weather_6hr[i]["observation_time"]["value"]) for i in range(0, len(self.weather_6hr))]
        temp_6hr = [self.weather_6hr[i]["temp"]["value"] for i in range(0, len(self.weather_6hr))]
        self.temperature_forecast_6hr = {time_6hr[i]: temp_6hr[i] for i in range(len(time_6hr))}
        logger.debug(f'Returning dictionary containing time:value pair, "self.temperature_forecast_6hr \n')
        return self.temperature_forecast_6hr

    # Class method get_temperature_now() returns a dictionary of the temperature against time
    def get_temperature_now(self):
        logger.debug(f'Function call: get_temperature_now()')
        self.temperature_forecast_now = {self.now_time: self.now_temperature}
        logger.debug(f'Returning dictionary containing time:value pair, "self.temperature_forecast_now \n')
        return self.temperature_forecast_now

# Precipitation

    # Class method get_precipitation_96hr() returns a dictionary of the precipitation against time
    def get_precipitation_96hr(self):
        logger.debug(f'Function call: get_precipitation_96hr()')
        time_96hr = [local_time(self.weather_96hr[i]["observation_time"]["value"]) for i in range(0, len(self.weather_96hr))]
        precipitation_96hr = [self.weather_96hr[i]["precipitation"]["value"] for i in range(0, len(self.weather_96hr))]
        self.precipitation_forecast_96hr = {time_96hr[i]: precipitation_96hr[i] for i in range(len(time_96hr))}
        logger.debug(f'Returning dictionary containing time:value pair, "self.precipitation_forecast_96hr \n')
        return self.precipitation_forecast_96hr

    # Class method get_precipitation_6hr() returns a dictionary of the temperature against time
    def get_precipitation_6hr(self):
        logger.debug(f'Function call: get_precipitation_6hr()')
        time_6hr = [local_time(self.weather_6hr[i]["observation_time"]["value"]) for i in range(0, len(self.weather_6hr))]
        precipitation_6hr = [self.weather_6hr[i]["precipitation"]["value"] for i in range(0, len(self.weather_6hr))]
        self.precipitation_forecast_6hr = {time_6hr[i]: precipitation_6hr[i] for i in range(len(time_6hr))}
        logger.debug(f'Returning dictionary containing time:value pair, "self.precipitation_forecast_6hr \n')
        return self.precipitation_forecast_6hr

    # Class method get_precipitation_now() returns a dictionary of the temperature against time
    def get_precipitation_now(self):
        logger.debug(f'Function call: get_precipitation_now()')
        self.precipitation_forecast_now = {self.now_time: self.now_precipitation}
        logger.debug(f'Returning dictionary containing time:value pair, "self.precipitation_forecast_now \n')
        return self.precipitation_forecast_now

# Precipitation type

    # Class method get_precipitation_type_96hr() returns a dictionary of the precipitation against time
    def get_precipitation_type_96hr(self):
        logger.debug(f'Function call: get_precipitation_type_96hr()')
        time_96hr = [local_time(self.weather_96hr[i]["observation_time"]["value"]) for i in range(0, len(self.weather_96hr))]
        precipitation_type_96hr = [self.weather_96hr[i]["precipitation_type"]["value"] for i in range(0, len(self.weather_96hr))]
        self.precipitation_type_forecast_96hr = {time_96hr[i]: precipitation_type_96hr[i] for i in range(len(time_96hr))}
        logger.debug(f'Returning dictionary containing time:value pair, "self.precipitation_type_forecast_96hr \n')
        return self.precipitation_type_forecast_96hr

    # Class method get_precipitation_type_6hr() returns a dictionary of the temperature against time
    def get_precipitation_type_6hr(self):
        logger.debug(f'Function call: get_precipitation_type_6hr()')
        time_6hr = [local_time(self.weather_6hr[i]["observation_time"]["value"]) for i in range(0, len(self.weather_6hr))]
        precipitation_type_6hr = [self.weather_6hr[i]["precipitation_type"]["value"] for i in range(0, len(self.weather_6hr))]
        self.precipitation_type_forecast_6hr = {time_6hr[i]: precipitation_type_6hr[i] for i in range(len(time_6hr))}
        logger.debug(f'Returning dictionary containing time:value pair, "self.precipitation_type_forecast_6hr \n')
        return self.precipitation_type_forecast_6hr

    # Class method get_precipitation_type_now() returns a dictionary of the temperature against time
    def get_precipitation_type_now(self):
        logger.debug(f'Function call: get_precipitation_type_now()')
        self.precipitation_type_forecast_now = {self.now_time: self.now_precipitation_type}
        logger.debug(f'Returning dictionary containing time:value pair, "self.precipitation_type_forecast_now \n')
        return self.precipitation_type_forecast_now

# Feels like

    # Class method get_feels_like_96hr() returns a dictionary of the precipitation against time
    def get_feels_like_96hr(self):
        logger.debug(f'Function call: get_feels_like_96hr()')
        time_96hr = [local_time(self.weather_96hr[i]["observation_time"]["value"]) for i in range(0, len(self.weather_96hr))]
        feels_like_96hr = [self.weather_96hr[i]["feels_like"]["value"] for i in range(0, len(self.weather_96hr))]
        self.feels_like_forecast_96hr = {time_96hr[i]: feels_like_96hr[i] for i in range(len(time_96hr))}
        logger.debug(f'Returning dictionary containing time:value pair, "self.feels_like_forecast_96hr \n')
        return self.feels_like_forecast_96hr

    # Class method get_precipitation_6hr() returns a dictionary of the temperature against time
    def get_feels_like_6hr(self):
        logger.debug(f'Function call: get_feels_like_6hr()')
        time_6hr = [local_time(self.weather_6hr[i]["observation_time"]["value"]) for i in range(0, len(self.weather_6hr))]
        feels_like_6hr = [self.weather_6hr[i]["feels_like"]["value"] for i in range(0, len(self.weather_6hr))]
        self.feels_like_forecast_6hr = {time_6hr[i]: feels_like_6hr[i] for i in range(len(time_6hr))}
        logger.debug(f'Returning dictionary containing time:value pair, "self.feels_like_forecast_6hr \n')
        return self.feels_like_forecast_6hr

    # Class method get_precipitation_now() returns a dictionary of the temperature against time
    def get_feels_like_now(self):
        logger.debug(f'Function call: get_feels_like_now()')
        self.feels_like_forecast_now = {self.now_time: self.now_feelslike}
        logger.debug(f'Returning dictionary containing time:value pair, "self.feels_like_forecast_now \n')
        return self.feels_like_forecast_now


# Wind speed

    # Class method get_wind_speed_96hr() returns a dictionary of the precipitation against time
    def get_wind_speed_96hr(self):
        logger.debug(f'Function call: get_wind_speed_96hr()')
        time_96hr = [local_time(self.weather_96hr[i]["observation_time"]["value"]) for i in range(0, len(self.weather_96hr))]
        wind_speed_96hr = [self.weather_96hr[i]["wind_speed"]["value"] for i in range(0, len(self.weather_96hr))]
        self.wind_speed_forecast_96hr = {time_96hr[i]: wind_speed_96hr[i] for i in range(len(time_96hr))}
        logger.debug(f'Returning dictionary containing time:value pair, "self.wind_speed_forecast_96hr \n')
        return self.wind_speed_forecast_96hr

    # Class method get_precipitation_6hr() returns a dictionary of the temperature against time
    def get_wind_speed_6hr(self):
        logger.debug(f'Function call: get_wind_speed_6hr()')
        time_6hr = [local_time(self.weather_6hr[i]["observation_time"]["value"]) for i in range(0, len(self.weather_6hr))]
        wind_speed_6hr = [self.weather_6hr[i]["wind_speed"]["value"] for i in range(0, len(self.weather_6hr))]
        self.wind_speed_forecast_6hr = {time_6hr[i]: wind_speed_6hr[i] for i in range(len(time_6hr))}
        logger.debug(f'Returning dictionary containing time:value pair, "self.wind_speed_forecast_6hr \n')
        return self.wind_speed_forecast_6hr

    # Class method get_precipitation_now() returns a dictionary of the temperature against time
    def get_wind_speed_now(self):
        logger.debug(f'Function call: get_wind_speed_now()')
        self.wind_speed_forecast_now = {self.now_time: self.now_windspeed}
        logger.debug(f'Returning dictionary containing time:value pair, "self.wind_speed_forecast_now \n')
        return self.wind_speed_forecast_now

get_resort_keys()

#     def checkSnow(self):
#         self.snowIn96hrForecast = [(self.weatherJson96hr[i]["precipitation"]["value"] if self.weatherJson96hr[i]["precipitation_type"]["value"] == "snow" else 0) for i in range(0, len(self.weatherJson96hr))]
#         # Calculates the amount of snow in the next 96hr
#         self.accumulatedSnow = 0
#         for snow in self.snowIn96hrForecast:
#             self.accumulatedSnow = float(snow) + self.accumulatedSnow
        
#         # Creates an attribute called self.isSnow to indicate to the user if there is snow or not
#         if self.accumulatedSnow > 0:
#             self.isSnow = True
#         else:
#             self.isSnow = False        

#     # This method  checks if there is snow in the next 4 days and prints it to the user
#     def print4DaySnow(self):
#         self.checkSnow()
#         if self.isSnow:
#             print(self.name + ": SNOW IN THE NEXT 4 DAYS")
#             print(f"{self.accumulatedSnow :.2f} mm of snow")
#             print("")
#         else:
#             print(self.name + ": NO SNOW IN THE NEXT 4 DAYS")
#             print("")

#     # This method takes the return values of queryByResort() and realTimeJson() as arguments and prints current forecast information
#     def printRealTimeWeather(self):
#         print(f"Location: {self.name}")
#         print(f"Time: {self.nowTime}")
#         print(f"Temperature: {self.nowTemp}°C")
#         print(f"Feels Like: {self.nowFeelsLike}°C")
#         print(f"Precipitation: {self.nowPrecipitation}mm")
#         print(f"Precipitation Type: {self.nowPrecipitationType}")
#         print(f"Wind Speed: {self.nowWindSpeed}m/s")
#         print(f"Wind Direction: {self.nowWindDirection}° (0° is North)")
#         print(f"Cloud Cover: {self.nowCloudCover}m")

#     # This method takes a weatherJson as an input and then plots the temperature against observation time


# # This method takes a country as an arg and returns a list of dicts of the resorts in that country (contains a list of dicts containing name, country, lat and lon information)
# def resortsInCountry(country):
#     with open(SKI_RESORT_JSON, "r") as f:
#         resortDictList = json.load(f)
#         resortsInCountry = [
#             resortDictList[resort]["name"]
#             for resort in resortDictList
#             if resortDictList[resort]["country"].lower() == country.lower()
#         ]
#         return resortsInCountry


# # Create a method takes the string of the country (only "Canada" or "USA" currently) as an arg and checks every resort in the country as listed in the json file to see if there is snow
# # TODO: Create a thread to make this run faster
# def queryByCountry(country):
#     with open(SKI_RESORT_JSON, "r") as f:
#         resortDictList = json.load(f)
#         for key in resortDictList:
#             if resortDictList[key]["country"].lower() == country.lower():
#                 resortObj = Resort(key)
#                 resortObj.print4DaySnow()

# resort = Resort("sunshine", "96hr")
# resort.print4DaySnow()
