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


ABS_PATH = os.path.abspath(__file__)
D_NAME = os.path.dirname(ABS_PATH)


# This method takes the string of a time in ISO 8601 format and converts it to local time using the system timezone
def localTime(UTCTime):
    return dp.parse(UTCTime).astimezone(
        get_localzone()
    )  # returns a datetime.datetime object


# This method adds a resort to the json file, returns the skiResort json file
def addNewResort(resortKey, resortName, country, lat, lon, *args):
    print(args)
    # Uses args to see if it is being run from the test file
    if args[0] == "test":
        testJsonPath = "..\\tests\\Resources\\test_skiResorts.json"
        addJson = testJsonPath
    else:
        addJson = SKI_RESORT_JSON

    newResortDict = {
        resortKey: {"name": resortName, "country": country, "lat": lat, "lon": lon}
    }
    with open(addJson, "r") as f:
        resortJson = json.load(f)
        resortJson.update(newResortDict)

    with open(addJson, "w") as f:
        json.dump(resortJson, f, indent=4)
        print(f"Added {resortName} successfully")

    return resortJson


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
    def __init__(self, resortKey, *args):
        # Check if you are in the current directory, if not, set it to the current directory
        currentDir = os.getcwd()

        if currentDir != D_NAME:
            os.chdir(D_NAME)
        else:
            pass

        # Checks if the user enters arguments to initiate json files or not
        self.dataJSON = SKI_RESORT_JSON
        self.args = args

        if not args:
            raise Exception("Invalid arg passed. Function arguments must contain one of '360min' and/or '96hr' and/or 'realtime'") # Note there is a hidden arg that is called test that does not access the api to do a mock test

        # Opens json file to get location parameters
        with open(SKI_RESORT_JSON, "r") as f:
            resortDictList = json.load(f)
            resortDict = resortDictList[resortKey]

        self.name = resortDict["name"]
        self.lon = resortDict["lon"]
        self.lat = resortDict["lat"]
        self.country = resortDict["country"]

        self.weatherJsonRealTime = {}
        self.weatherJson360Min = {}
        self.weatherJson96hr = {}



    def processRequests(self):
        for requestItem in self.args:
            # Makes a request for realtime data
            if requestItem == "realtime":
                self.requestRealtime()

            # Makes a request for 360min forecast and stores in self.weatherJson360Min
            elif requestItem == "360min":
                self.request360min()

            # Makes a request for 4 day (96hr) forecast and stores in self.weatherJson96hr
            elif requestItem == "96hr":
                self.request96hr()

    # Requests realtime data
    def requestRealtime(self):
        querystring = {
            "lat": str(self.lat),
            "lon": str(self.lon),
            "unit_system": "si",
            "fields": "precipitation,precipitation_type,temp,feels_like,wind_speed,wind_direction,sunrise,sunset,visibility,cloud_cover,cloud_base,weather_code",
            "apikey": CLIMACELL_KEY,
        }

        response = requests.request("GET", URL_REALTIME, params=querystring)

        if response.ok:
            self.weatherJsonRealTime = json.loads(response.text)
        else:
            return "Bad response"

        self.nowTime = localTime(self.weatherJsonRealTime["observation_time"]["value"])
        self.nowTemp = self.weatherJsonRealTime["temp"]["value"]
        self.nowFeelsLike = self.weatherJsonRealTime["feels_like"]["value"]
        self.nowPrecipitation = self.weatherJsonRealTime["precipitation"]["value"]
        self.nowPrecipitationType = self.weatherJsonRealTime["precipitation_type"]["value"]
        self.nowWindSpeed = self.weatherJsonRealTime["wind_speed"]["value"]
        self.nowWindDirection = self.weatherJsonRealTime["wind_direction"]["value"]
        self.nowCloudCover = self.weatherJsonRealTime["cloud_cover"]["value"]

        return self.weatherJsonRealTime   

    def request360min(self):
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
            self.weatherJson360Min = json.loads(response.text)
        else:
            return "Bad response"
        
        return self.weatherJson360Min
        
    def request96hr(self):
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
            self.weatherJson96hr = json.loads(response.text)
        else:
            return "Bad response"
             
        return self.weatherJson96hr

     
    def checkSnow(self):

        self.snowIn96hrForecast = [(self.weatherJson96hr[i]["precipitation"]["value"] if self.weatherJson96hr[i]["precipitation_type"]["value"] == "snow" else 0) for i in range(0, len(self.weatherJson96hr))]
        # Calculates the amount of snow in the next 96hr
        self.accumulatedSnow = 0
        for snow in self.snowIn96hrForecast:
            self.accumulatedSnow = float(snow) + self.accumulatedSnow
        
        # Creates an attribute called self.isSnow to indicate to the user if there is snow or not
        if self.accumulatedSnow > 0:
            self.isSnow = True
        else:
            self.isSnow = False        

    # This method  checks if there is snow in the next 4 days and prints it to the user
    def print4DaySnow(self):
        self.checkSnow()
        if self.isSnow:
            print(self.name + ": SNOW IN THE NEXT 4 DAYS")
            print(f"{self.accumulatedSnow :.2f} mm of snow")
            print("")
        else:
            print(self.name + ": NO SNOW IN THE NEXT 4 DAYS")
            print("")

    # This method takes the return values of queryByResort() and realTimeJson() as arguments and prints current forecast information
    def printRealTimeWeather(self):
        print(f"Location: {self.name}")
        print(f"Time: {self.nowTime}")
        print(f"Temperature: {self.nowTemp}°C")
        print(f"Feels Like: {self.nowFeelsLike}°C")
        print(f"Precipitation: {self.nowPrecipitation}mm")
        print(f"Precipitation Type: {self.nowPrecipitationType}")
        print(f"Wind Speed: {self.nowWindSpeed}m/s")
        print(f"Wind Direction: {self.nowWindDirection}° (0° is North)")
        print(f"Cloud Cover: {self.nowCloudCover}m")

    # This method takes a weatherJson as an input and then plots the temperature against observation time


# This method takes a country as an arg and returns a list of dicts of the resorts in that country (contains a list of dicts containing name, country, lat and lon information)
def resortsInCountry(country):
    with open(SKI_RESORT_JSON, "r") as f:
        resortDictList = json.load(f)
        resortsInCountry = [
            resortDictList[resort]["name"]
            for resort in resortDictList
            if resortDictList[resort]["country"].lower() == country.lower()
        ]
        return resortsInCountry


# Create a method takes the string of the country (only "Canada" or "USA" currently) as an arg and checks every resort in the country as listed in the json file to see if there is snow
# TODO: Create a thread to make this run faster
def queryByCountry(country):
    with open(SKI_RESORT_JSON, "r") as f:
        resortDictList = json.load(f)
        for key in resortDictList:
            if resortDictList[key]["country"].lower() == country.lower():
                resortObj = Resort(key)
                resortObj.print4DaySnow()

resort = Resort("sunshine", "96hr")
resort.print4DaySnow()
