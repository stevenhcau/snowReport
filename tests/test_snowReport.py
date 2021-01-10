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
abspath = os.path.abspath(__file__)
dname = os.path.dirname(abspath)
os.chdir(dname)

testJsonPath = os.path.join(abspath, "\\test_skiResorts.json")

# To determine snowAppPath
snowAppPath = "..\\snowApp\\skiResorts.json"

class testSnowReport(unittest.TestCase):

    # This is useful when you want to do something once but is too costly to do before each test
    # For example, you can use this to set up a database, in this case, we will be using this classmethod in order to set up the JSON file, and then we will delete the JSON file in the tearDownClass section
    # To set up the database, a copy of the skiResorts.json file will be made and named to a copy file, which will be used to reproduce the original file in the end
    # This is not very elegant and there might be a better way to to do this
    # This classmethod will also set up an object of our Resort class
    @classmethod
    def setUpClass(cls):
        pass

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

        with open(testJsonPath, "r") as f:
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

    # @patch("snowApp.snowReport.Resort.print4DaySnow")
    # def test_print4DaySnow_True(self):
    #     with patch.object(snowReport.Resort,"__init__"):
    #         mockResort = snowReport.Resort(None)
    #         mockResort.name = "Mock Resort"
    #         mockResort.isSnow = 1
    #         mockResort.accumulatedSnow = 2
    #     assert_true(True)

        
# TODO: Mock and unit test requests: https://realpython.com/testing-third-party-apis-with-mocks/
# TODO: Mock article: https://aaronlelevier.github.io/python-unit-testing-with-magicmock/
# TODO: Mock artcile: https://medium.com/@george.shuklin/mocking-complicated-init-in-python-6ef9850dd202



if __name__ == "__main__":
    unittest.main()
