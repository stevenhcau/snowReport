#!/usr/bin/env python3

import datetime
import json
import os
import snowReport
import unittest

"""
This module is used to complete unit testing and automated testing for snowReport.py
Note: We can import the snowReport module easily because it is in the same directory
"""


class testSnowReport(unittest.TestCase):

    # This is useful when you want to do something once but is too costly to do before each test
    # For example, you can use this to set up a database, in this case, we will be using this classmethod in order to set up the JSON file, and then we will delete the JSON file in the tearDownClass section
    # To set up the database, a copy of the skiResorts.json file will be made and named to a copy file, which will be used to reproduce the original file in the end
    # This is not very elegant and there might be a better way to to do this
    # This classmethod will also set up an object of our Resort class
    @classmethod
    def setUpClass(cls):
        # Opens the existing json file and closes after using it
        with open("skiResorts.json") as f:
            skiResortData = json.load(f)

        # Creates a copy json file containing the data from the original skiResorts.json file
        with open("copy_skiResorts.json", "w") as f:
            json.dump(skiResortData, f, indent=4)

        # testResortObject = snowReport.Resort("test_Location (Banff)")

    # Recreates skiResorts.json file containing the original data before the tests, and then deletes the copy_skiResorts.json file
    @classmethod
    def tearDownClass(cls):
        with open("copy_skiResorts.json",) as f:
            originalSkiResortData = json.load(f)

        os.remove("skiResorts.json")

        with open("skiResorts.json", "w") as f:
            json.dump(originalSkiResortData, f, indent=4)

        os.remove("copy_skiResorts.json")

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
        snowReport.addNewResort(
            "testResortKey - Calgary", "Calgary", "Canada", "51.0447", "-114.066666",
        )
        with open("skiResorts.json", "r") as f:
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


if __name__ == "__main__":
    unittest.main()

