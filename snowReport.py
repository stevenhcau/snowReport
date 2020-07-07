#!/usr/bin/env python3

# Requests is used to access api
# JSON is used to parse API response from JSON format into a list of dictionaries
# os is used to set current directory and folder structure
# dateutil.parser as dp is used to convert UTC format into datetime format
# datetime and tzlocal is used to convert UTC timezone into Canada/Mountain Time

# QUESTION: Is this alphabetical, do you do it based on module name?


from datetime import datetime
import dateutil.parser as dp
import json, os, requests
import matplotlib.pyplot as plt
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

    The program 

Using climacell API for weather data. API key: G6pKgE1QNQqjkSM5XzBZMW5N7cPgxUVy
skiResort data is stored in skiResorts.json
"""
# GLOBAL VARS
URL_HOURLY = "https://api.climacell.co/v3/weather/forecast/hourly"
URL_NOWCAST = "https://api.climacell.co/v3/weather/nowcast"
URL_REALTIME = "https://api.climacell.co/v3/weather/realtime"
SKI_RESORT_JSON = "skiResorts.json"
CLIMACELL_KEY = "G6pKgE1QNQqjkSM5XzBZMW5N7cPgxUVy"

# This method takes the string of a time in ISO 8601 format and converts it to local time using the system timezone
def localTime(UTCTime):
    return dp.parse(UTCTime).astimezone(
        get_localzone()
    )  # returns a datetime.datetime object


# This method adds a resort to the json file, returns the skiResort json file
def addNewResort(resortKey, resortName, country, lat, lon):
    newResortDict = {
        resortKey: {"name": resortName, "country": country, "lat": lat, "lon": lon}
    }
    with open(SKI_RESORT_JSON, "r") as f:
        skiResorts = json.load(f)
        print(skiResorts)
        skiResorts.update(newResortDict)
        print(f"Added {resortName} successfully")
        return skiResorts


# Defines a class "Resort" to handle the attributes and methods for each ski resort
class Resort:
    def __init__(self, resortKey):
        # Opens json file to get location parameters
        with open(SKI_RESORT_JSON, "r") as f:
            resortDictList = json.load(f)
            resortDict = resortDictList[resortKey]

        self.name = resortDict["name"]
        self.lon = resortDict["lon"]
        self.lat = resortDict["lat"]
        self.country = resortDict["country"]

        # Makes a request for 4 day (96hr) forecast and stores in self.weatherJson96hr
        querystring = {
            "lat": str(self.lat),
            "lon": str(self.lon),
            "unit_system": "si",
            "start_time": "now",
            "fields": "precipitation,temp,feels_like,humidity,wind_speed,wind_direction,precipitation_type,precipitation_probability,sunrise,sunset,cloud_cover,cloud_base,weather_code",
            "apikey": CLIMACELL_KEY,
        }
        response = requests.request(
            "GET", URL_HOURLY, params=querystring
        )  # ClimaCell: The hourly call provides a global hourly forecast, up to 96 hours (4 days) out, for a specific location.
        self.weatherJson96hr = json.loads(response.text)

        # This is causing an error - if there is no snow then in returns an empty list
        self.snowForecast96hr = [
            self.weatherJson96hr[i]["precipitation"]["value"]
            for i in range(0, len(self.weatherJson96hr))
            if self.weatherJson96hr[i]["precipitation_type"]["value"] == "snow"
        ]

        # Makes a request for realtime forecast and stores in self.weatherJsonTime
        querystring = {
            "lat": str(resortDict["lat"]),
            "lon": str(resortDict["lon"]),
            "unit_system": "si",
            "fields": "precipitation,precipitation_type,temp,feels_like,wind_speed,wind_direction,sunrise,sunset,visibility,cloud_cover,cloud_base,weather_code",
            "apikey": CLIMACELL_KEY,
        }
        response = requests.request("GET", URL_REALTIME, params=querystring)
        self.weatherJsonRealTime = json.loads(response.text)

        self.nowTime = localTime(self.weatherJsonRealTime["observation_time"]["value"])
        self.nowTemp = self.weatherJsonRealTime["temp"]["value"]
        self.nowFeelsLike = self.weatherJsonRealTime["feels_like"]["value"]
        self.nowPrecipitation = self.weatherJsonRealTime["precipitation"]["value"]
        self.nowPrecipitationType = self.weatherJsonRealTime["precipitation_type"][
            "value"
        ]
        self.nowWindSpeed = self.weatherJsonRealTime["wind_speed"]["value"]
        self.nowWindDirection = self.weatherJsonRealTime["wind_direction"]["value"]
        self.nowCloudCover = self.weatherJsonRealTime["cloud_cover"]["value"]

        # Makes a request for 360min forecast and stores in self.weatherJson360Min
        querystring = {
            "lat": str(resortDict["lat"]),
            "lon": str(resortDict["lon"]),
            "unit_system": "si",
            "timestep": "5",
            "start_time": "now",
            "fields": "temp,feels_like,humidity,wind_speed,wind_direction,precipitation,precipitation_type,sunrise,sunset,visibility,cloud_cover,cloud_base,weather_code",
            "apikey": CLIMACELL_KEY,
        }
        response = requests.request("GET", URL_NOWCAST, params=querystring)
        self.weatherJson360Min = json.loads(response.text)

    # This method  checks if there is snow in the next 4 days. If the length of list snowForecast96hr is greater than 0, there will be at least some amount of snow in the next 4 days
    # This method is specific to the 4 hour forecast because of the format of the json data
    def checkSnow96hr(self):
        if len(self.snowForecast96hr) > 0:
            return True
        else:
            return False

    # This method calculates the accumulated snow in the next 4 days
    def totalSnow96hr(self):
        accumulatedSnow = 0
        for snow in self.snowForecast96hr:
            accumulatedSnow = float(snow) + accumulatedSnow
        return accumulatedSnow

    # This method  checks if there is snow in the next 4 days and prints it to the user
    def print4DaySnow(self):
        if len(self.snowForecast96hr) > 0:
            print(self.name + ": SNOW IN THE NEXT 4 DAYS")
            print(f"{self.totalSnow96hr():.2f} mm of snow")
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

    def plotTemp(self, forecast):
        if forecast == "96hr":
            x = [
                localTime(self.weatherJson96hr[i]["observation_time"]["value"])
                for i in range(0, len(self.weatherJson96hr))
            ]
            y = [
                self.weatherJson96hr[i]["temp"]["value"]
                for i in range(0, len(self.weatherJson96hr))
            ]
        elif forecast == "360min":
            x = [
                localTime(self.weatherJson360Min[i]["observation_time"]["value"])
                for i in range(0, len(self.weatherJson360Min))
            ]
            y = [
                self.weatherJson360Min[i]["temp"]["value"]
                for i in range(0, len(self.weatherJson360Min))
            ]

        # Step through the temperatures to y limit for temperatures. The lower or upper limit must always be 0

        if min(y) < -30:
            ymin = -40
        elif min(y) < -20:
            ymin = -30
        elif min(y) < -10:
            ymin = -20
        elif min(y) < 0:
            ymin = -10
        else:
            ymin = 0

        if max(y) > 30:
            ymax = 40
        elif max(y) > 20:
            ymax = 30
        elif max(y) > 10:
            ymax = 20
        elif max(y) > 0:
            ymax = 10
        else:
            ymax = 0

        plt.style.use("ggplot")
        plt.plot(x, y, marker="o", linestyle="-")
        plt.title("Temperature (°C) vs. Time")

        # Set y axis scale and x and y labels
        plt.ylim(ymin, ymax)
        plt.xlabel("Observation Time")
        plt.ylabel("Temperature (°C)")
        plt.gcf().set_size_inches(12, 7)

        plt.show()

    # This method takes a weatherJson as an input and then plots the preciptation amount against observation time
    def plotPrecipitation(self, forecast):
        if forecast == "96hr":
            x = [
                localTime(self.weatherJson96hr[i]["observation_time"]["value"])
                for i in range(0, len(self.weatherJson96hr))
            ]
            y = [
                self.weatherJson96hr[i]["precipitation"]["value"]
                for i in range(0, len(self.weatherJson96hr))
            ]
        elif forecast == "360min":
            x = [
                localTime(self.weatherJson360Min[i]["observation_time"]["value"])
                for i in range(0, len(self.weatherJson360Min))
            ]
            y = [
                self.weatherJson360Min[i]["precipitation"]["value"]
                for i in range(0, len(self.weatherJson360Min))
            ]

        plt.style.use("ggplot")
        plt.plot(x, y, marker="o", linestyle="-")
        plt.title("Precipitation (mm) vs. Time")

        # Set y axis scale and x and y labels
        plt.xlabel("Observation Time")
        plt.ylabel("Preciptation (mm)")
        plt.gcf().set_size_inches(12, 7)

        plt.show()


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


# Main function that grabs CLI args, then forecasts based on args
# First arg will take usage (realtime/96hr/360min)
# Second arg will take the keylist or resort

queryByCountry("Canada")

# def main():
#     try:
#         usage = sys.argv[1].lower()
#     except:
#         print("Not run from command line")
#         print("Please enter usage scenario") # print out the different usage scenario options
#         usage = input().lower()
#         print('')
#     try:
#         resortFilter = sys.argv[2].lower() # location filter: favorites, alberta, canada, usa
#     except:
#         print("Not run from command line")
#         print("Please enter filter request") # print out the different filter request
#         resortFilter = input().lower()
#         print('')

#     # TODO: Create try and except for the arguments
#     # TODO: Create a function and pass it a list of resorts to execute
#     favorites = ["lakeLouise", "sunshine", "fernie", "revelstoke", "whistler"]
#     albertaResorts = ["lakeLouise", "sunshine", "nakiska", "castleMountain", "norquay"]
#     # Add threads to optimize the request option

#     if resortFilter.lower() == "favorites":
#         if usage == "realtime":
#             for resort in favorites:
#                 resortObj = Resort(resort)
#                 resortObj.printRealTimeWeather
#         elif usage == "4day":

#             for resort in favorites:
#                 resortObj = Resort(resort)
#                 resortObj.print4DaySnow
#         elif usage == "96hr":
#             for resort in favorites:
#                 resortObj = Resort(resort)
#                 resortObj.print4DaySnow
#         elif usage == "360min":
#             for resort in favorites:
#                 resortObj = Resort(resort)
#                 resortObj.plotTemp()
#                 resortObj.plotPrecipitation()

#     elif resortFilter.lower() == "alberta":
#         if usage == "realtime":
#             for resort in albertaResorts:
#                 resortObj = Resort(resort)
#                 resortObj.printRealTimeWeather
#         elif usage == "4day":
#             for resort in albertaResorts:
#                 resortObj = Resort(resort)
#                 resortObj.print4DaySnow
#         elif usage == "96hr":
#             for resort in albertaResorts:
#                 resortObj = Resort(resort)
#                 resortObj.print4DaySnow
#         elif usage == "360min":
#             for resort in albertaResorts:
#                 resortObj = Resort(resort)
#                 resortObj.plotTemp()
#     elif usage == "canada":
#         queryByCountry("Canada")

#     elif usage == "usa":
#         queryByCountry("USA")

#     else:
#         print("")

# if __name__ == '__main__':
#     main()
