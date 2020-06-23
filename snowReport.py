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

'''
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
'''
# GLOBAL VARS
URL_HOURLY = "https://api.climacell.co/v3/weather/forecast/hourly"
URL_NOWCAST = "https://api.climacell.co/v3/weather/nowcast"
URL_REALTIME = "https://api.climacell.co/v3/weather/realtime"
SKI_RESORT_JSON = 'skiResorts.json'
CLIMACELL_KEY = "G6pKgE1QNQqjkSM5XzBZMW5N7cPgxUVy"

# This method takes the string of a time in ISO 8601 format and converts it to local time using the system timezone
def localTime(UTCTime):
    return dp.parse(UTCTime).astimezone(get_localzone())   # returns a datetime.datetime object

# This method adds a resort to the json file, returns the skiResort json file
def addNewResort(resortKey, resortName, country, lat, lon):
    newResortDict = {resortKey: {"name": resortName, "country": country, "lat": lat, "lon": lon}}
    with open(SKI_RESORT_JSON, 'r') as f:
        skiResorts = json.load(f)
        print(skiResorts)
        skiResorts.update(newResortDict)
        print(f"Added {resortName} successfully")
        return skiResorts

# This method takes the resort name as an arg and returns the dictionary for the resort (contains name, country, lat and lon information)
def queryByResort(resortSearch):
    with open(SKI_RESORT_JSON, 'r') as f:
        resortDictList = json.load(f)
        resortDict = resortDictList[resortSearch]
        return resortDict
# This method takes a country as an arg and returns a list of dicts of the resorts in that country (contains a list of dicts containing name, country, lat and lon information)
def queryByCountry(country):
    with open(SKI_RESORT_JSON, 'r') as f:
        resortDictList = json.load(f)
        resortsInCountry = [resortDictList[resort] for resort in resortDictList if resortDictList[resort]["country"] == country] 
        return resortsInCountry

# This API call gets information for every hour, resulting in a dataset of 108
# This method takes a dictionary containing the location information as an argument and retrieves the json from the API
def forecast96hr(resortDict): 
    querystring = {"lat":str(resortDict['lat']),"lon":str(resortDict['lon']),"unit_system":"si","start_time":"now","fields":"precipitation,temp,feels_like,humidity,wind_speed,wind_direction,precipitation_type,precipitation_probability,sunrise,sunset,cloud_cover,cloud_base,weather_code","apikey":CLIMACELL_KEY}
    response = requests.request("GET", URL_HOURLY, params=querystring) # ClimaCell: The hourly call provides a global hourly forecast, up to 96 hours (4 days) out, for a specific location.
    weatherJson96hr = json.loads(response.text)
    return weatherJson96hr

# This method determines if there is snow in the 4 hour forecast. If the snowAmount is greater than 0, there will be at least some amount of snow in the next 4 days
# This method is specific to the 4 hour forecast because of the format of the json data
def checkForSnow(weatherJson96hr):
    snowAmount = [weatherJson96hr[i]["precipitation"]["value"] for i in range(0, len(weatherJson96hr)) if weatherJson96hr[i]["precipitation_type"]["value"] == "snow"]
    if len(snowAmount) > 0:
        return True
    else:
        return False

# This method takes the json data for the next 4 days and prints the amount of snow expected
def snowAmount96hr(weatherJson96hr):
    snowAmount = [weatherJson96hr[i]["precipitation"]["value"] for i in range(0, len(weatherJson96hr)) if weatherJson96hr[i]["precipitation_type"]["value"] == "snow"]
    accumulatedSnow = 0
    for snow in snowAmount:
        accumulatedSnow = float(snow) + accumulatedSnow
    return accumulatedSnow

# This method takes the return value of queryByResort() and weatherJson96hr() and checks if there is snow in the next 4 days
def display4DaySnow(resortDict, weatherJson96hr):
    if checkForSnow(weatherJson96hr) is True:
        print(resortDict["name"] + ": SNOW IN THE NEXT 4 DAYS")
        print(f"{snowAmount96hr(weatherJson96hr):.2f} mm of snow")
        print('')
    else:
        print(resortDict["name"] + ": NO SNOW IN THE NEXT 4 DAYS")
        print('')

# This method takes the string of the country (only "Canada" or "USA" currently) as an arg and checks every resort in the country as listed in the json file to see if there is snow
def printForecast96hrByCountry(country):
    for resort in queryByCountry(country):
        display4DaySnow(resort, forecast96hr(resort))

# ClimaCell: The realtime call provides observational data at the present time, down to the minute, for a specific location.
# This method takes the return from queryByResort() as an argument and returns a json data
def realTimeJson(resortDict):
    querystring = {"lat":str(resortDict['lat']),"lon":str(resortDict['lon']),"unit_system":"si","fields":"precipitation,precipitation_type,temp,feels_like,wind_speed,wind_direction,sunrise,sunset,visibility,cloud_cover,cloud_base,weather_code","apikey":CLIMACELL_KEY}
    response = requests.request("GET", URL_REALTIME, params=querystring)
    weatherJsonRealTime = json.loads(response.text)
    return weatherJsonRealTime

# This method takes the return values of queryByResort() and realTimeJson() as arguments and prints current forecast information
def printRealTimeWeather(resortDict, weatherJsonRealTime):
    print(f'Location: {resortDict["name"]}')
    print(f'Time: {localTime(weatherJsonRealTime["observation_time"]["value"])}')
    print(f'Temperature: {weatherJsonRealTime["temp"]["value"]}°C')
    print(f'Feels Like: {weatherJsonRealTime["feels_like"]["value"]}°C')
    print(f'Precipitation: {weatherJsonRealTime["precipitation"]["value"]}mm')
    print(f'Precipitation Type: {weatherJsonRealTime["precipitation_type"]["value"]}')
    print(f'Wind Speed: {weatherJsonRealTime["wind_speed"]["value"]}m/s')
    print(f'Wind Direction: {weatherJsonRealTime["wind_direction"]["value"]}° (0° is North)')
    print(f'Cloud Cover: {weatherJsonRealTime["cloud_cover"]["value"]}m')

# ClimaCell: The nowcast call provides forecasting data on a minute-­by-­minute basis, based on ClimaCell’s proprietary sensing technology and models.
# This API call asks for information for every 5 minutes, resulting in a data set of 72 for a total of 360 minutes
# This method takes a dictionary containing the location information as an argument and retrieves the json from the API
def forecast360min(resortDict):
    querystring = {"lat":str(resortDict['lat']),"lon":str(resortDict['lon']),"unit_system":"si","timestep":"5","start_time":"now","fields":"temp,feels_like,humidity,wind_speed,wind_direction,precipitation,precipitation_type,sunrise,sunset,visibility,cloud_cover,cloud_base,weather_code","apikey":CLIMACELL_KEY}
    response = requests.request("GET", URL_NOWCAST, params=querystring)
    weatherJson360Min = json.loads(response.text)
    return weatherJson360Min

# This method takes a weatherJson as an input and then plots the temperature against observation time
def plotTemp(weatherJson):
    x = [localTime(weatherJson[i]["observation_time"]["value"]) for i in range(0, len(weatherJson))]
    y = [weatherJson[i]['temp']["value"] for i in range(0, len(weatherJson))]

    # Step through the temperatures to y limit for temperatures. The lower or upper limit must always be 0
    if min(y) > 0:
        ymin = 0
    elif min(y) < -30:
        ymin = -40
    elif min(y) < -20:
        ymin = -30
    elif min(y) < -10:
        ymin = -20
    elif min(y) < 0:
        ymin = -10
    
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

    plt.style.use('ggplot') 
    plt.plot(x, y, marker = 'o', linestyle = '-')
    plt.title('Temperature (°C) vs. Time')

    # Set y axis scale and x and y labels
    plt.ylim(ymin, ymax)
    plt.xlabel('Observation Time')
    plt.ylabel('Temperature (°C)')
    plt.gcf().set_size_inches(12,7)

    plt.show()

# This method takes a weatherJson as an input and then plots the preciptation amount against observation time
def plotPrecipitation(weatherJson):
    x = [localTime(weatherJson[i]["observation_time"]["value"]) for i in range(0, len(weatherJson))]
    y = [weatherJson[i]['precipitation']["value"] for i in range(0, len(weatherJson))]
    plt.style.use('ggplot')
    plt.plot(x, y, marker = 'o', linestyle = '-')
    plt.title('Precipitation (mm) vs. Time')

    # Set y axis scale and x and y labels
    plt.xlabel('Observation Time')
    plt.ylabel('Preciptation (mm)')
    plt.gcf().set_size_inches(12,7)

    plt.show()

plotTemp(forecast360min(queryByResort("sunshine")))

# TODO: Open JSON file and get filter through the resorts, pick which resorts to search for data for based on location requested

# TODO: Create main function that grabs CLI args, then forecasts based on args

# forecast96hr(sunshine)
# forecast96hr(revelstoke)
# forecast96hr(lakeLouise)