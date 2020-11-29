#!/usr/bin/env python3

from datetime import date, datetime
import unittest
import snowReport

"""
This module is used to complete unit testing and automated testing for snowReport.py
Note: We can import the snowReport module easily because it is in the same directory
"""


class testSnowReport(unittest.TestCase):

    # Unit test methods must start with "test_", the naming convention is required so that python knows which method represents tests
    # Positive test, if the function returns a datetime.date object, then the method runs as expected
    def test_localTimeType(self):
        if type(snowReport.localTime("2020-05-15T21:00:00.000Z")) is not datetime.date:
            raise TypeError(
                "arg must be datetime.date, not a %s"
                % type(snowReport.localTime("2020-05-15T21:00:00.000Z"))
            )


if __name__ == "__main__":
    unittest.main()

