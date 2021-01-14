#!/usr/bin/env python3

import datetime
import json
from nose.tools import assert_true 
from mock import patch, MagicMock, PropertyMock
import os
import requests
import sys
import unittest


# This sets up the sys.path to tell the system where to look for packages. It adds the current working directory (snowReportApp) to the highest level to sys.path
# TODO: Update in setup.py to add to PYTHONPATH when finally creating the package, do this when the app is complete and we are setting up the setup.py file
sys.path.append(os.getcwd())

# Then it opens the module from the snowApp directory
from snowApp import snowReport

"""
This module is used to complete unit testing and automated testing for snowReport.py
Note: We can import the snowReport module easily because it is in the same directory
"""
URL_HOURLY = "https://api.climacell.co/v3/weather/forecast/hourly"
URL_NOWCAST = "https://api.climacell.co/v3/weather/nowcast"
URL_REALTIME = "https://api.climacell.co/v3/weather/realtime"
SKI_RESORT_JSON = "skiResorts.json"
CLIMACELL_KEY = "G6pKgE1QNQqjkSM5XzBZMW5N7cPgxUVy"

# Setting current working directory to ..\tests so that to easily access the resources files
ABS_PATH = os.path.abspath(__file__)
D_NAME = os.path.dirname(ABS_PATH)
os.chdir(D_NAME)

# To determine snowAppPath
snowAppPath = "..\\snowApp\\skiResorts.json"

# Set up the test json variables
with open(".\\Resources\\test_96hrJson.json", "r") as f:
    test96hrDict = json.load(f)

with open(".\\Resources\\test_360minJson.json", "r") as f:
    test360minDict = json.load(f)

with open(".\\Resources\\test_realtimeJson.json", "r") as f:
    testrealtimeDict = json.load(f)

class testSnowReport(unittest.TestCase):

    # This is useful when you want to do something once but is too costly to do before each test
    # For example, you can use this to set up a database, in this case, we will be using this classmethod in order to set up the JSON file, and then we will delete the JSON file in the tearDownClass section
    # To set up the database, a copy of the skiResorts.json file will be made and named to a copy file, which will be used to reproduce the original file in the end
    # This is not very elegant and there might be a better way to to do this
    # This classmethod will also set up an object of our Resort class
    @classmethod
    def setUpClass(cls):
        test_ResortClass = snowReport.Resort("test_Location (Banff)", "96hr", "realtime", "360min")
        print(test_ResortClass.lat)
        os.chdir(D_NAME) # Set the directory back to D_NAME because that the snowReport.Resort class changes it's class

    # Recreates skiResorts.json file containing the original data before the tests, and then deletes the copy_skiResorts.json file
    @classmethod
    def tearDownClass(cls):
        pass

    # Unit test methods must start with "test_", the naming convention is required so that python knows which method represents tests
    # Positive test, if the function returns a datetime.datetime object, then the method runs as expected
    # (Question) - why is the object datetime.datetime and not datetime.date?

    def test_localTimeType(self):
        if (
            type(snowReport.localTime("2020-05-15T21:00:00.000Z"))
            is not datetime.datetime
        ):
            raise TypeError(
                "arg must be a datetime.date, not a %s"
                % type(snowReport.localTime("2020-05-15T21:00:00.000Z"))
            )

    # Unit test adds a test resort (location Calgary) and accesses the json to see if it works
    def test_addNewResort(self):
        snowReport.addNewResort("testResortKey - Calgary", "Calgary", "Canada", "51.0447", "-114.066666", "test")

        with open(".\\Resources\\test_skiResorts.json", "r") as f:
            resortDictList = json.load(f)
            resortDict = resortDictList["testResortKey - Calgary"]
            self.resortName = resortDict["name"]
            self.resortLon = resortDict["lon"]
            self.resortLat = resortDict["lat"]
            self.resortCountry = resortDict["country"]

        self.assertEqual(self.resortName, "Calgary")
        self.assertEqual(self.resortLon, "-114.066666")
        self.assertEqual(self.resortLat, "51.0447")
        self.assertEqual(self.resortCountry, "Canada")

    # Tests the request for realtime weather data
    def test_realtimeRequest(self):
        querystring = {
                    "lat": "51.0447",
                    "lon": "-114.066666",
                    "unit_system": "si",
                    "fields": "precipitation,precipitation_type,temp,feels_like,wind_speed,wind_direction,sunrise,sunset,visibility,cloud_cover,cloud_base,weather_code",
                    "apikey": CLIMACELL_KEY,
                }

        response = requests.request("GET", URL_REALTIME, params=querystring)     
        assert_true(response.ok)
        
     # Tests the request for 96hr weather data   
    def test_96hrRequest(self):
        querystring = {
                    "lat": "51.0447",
                    "lon": "-114.066666",
                    "unit_system": "si",
                    "start_time": "now",
                    "fields": "precipitation,temp,feels_like,humidity,wind_speed,wind_direction,precipitation_type,precipitation_probability,sunrise,sunset,cloud_cover,cloud_base,weather_code",
                    "apikey": CLIMACELL_KEY,
                }

        response = requests.request("GET", URL_HOURLY, params=querystring)
        assert_true(response.ok)

     # Tests the request for 360min weather data   
    def test_360minRequest(self):
        querystring = {
                    "lat": "51.0447",
                    "lon": "-114.066666",
                    "unit_system": "si",
                    "fields": "temp,feels_like,humidity,wind_speed,wind_direction,precipitation,precipitation_type,sunrise,sunset,visibility,cloud_cover,cloud_base,weather_code",
                    "apikey": CLIMACELL_KEY,
                }

        response = requests.request("GET", URL_NOWCAST, params=querystring)
        assert_true(response.ok)

# TODO: Call on the function that does the request and then test it
    def test_request96hr(self):
        # Mock where it is accessed, not where it used: It is accessed in package snowApp from module snowReport
        # Here we are trying to mock the requests.request of the package snowApp from the module snowReport
        # We want to mock the object where it is actually used (it is used in the snowReport module)
        with patch("snowApp.snowReport.requests.request") as mocked_request:
            mocked_request.return_value.ok = True            
            mocked_request.return_value.request = test96hrDict

    def test_request360min(self):
        with patch("snowApp.snowReport.requests.request") as mocked_request:
            mocked_request.return_value.ok = True
            mocked_request.return_value.request = test360minDict

    def test_requestRealtime(self):
        with patch("snowApp.snowReport.requests.request") as mocked_request:
            mocked_request.return_value.ok = True
            mocked_request.return_value.request = testrealtimeDict
        
# TODO: Mock and unit test requests: https://realpython.com/testing-third-party-apis-with-mocks/
# TODO: Mock article: https://aaronlelevier.github.io/python-unit-testing-with-magicmock/
# TODO: Mock article: https://medium.com/@george.shuklin/mocking-complicated-init-in-python-6ef9850dd202
# TODO: Mock article: https://medium.com/@yeraydiazdiaz/what-the-mock-cheatsheet-mocking-in-python-6a71db997832


if __name__ == "__main__":
    unittest.main()
