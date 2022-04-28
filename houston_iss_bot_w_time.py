# Import necessary libraries

import json
import urllib.request
import os
import math
from time import sleep
from datetime import datetime
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt

# Keys and Secrets for the server

consumer_key = environ['consumer_key']
consumer_secret = environ['consumer_secret']
access_token = environ['access_token']
access_secret = environ['access_secret']

auth = tp.OAuthHandler(consumer_key, consumer_secret)
auth.set_access_token(access_token, access_secret)
api = tp.API(auth)

text = "Look to the Skies! The ISS is over Houston"

# Current position function, returns the current position of the ISS with the ISS API URL as an input

def current_position(url):
    response = urllib.request.urlopen(url)
    result = json.loads(response.read())
    location = result['iss_position']
    lat = float(location['latitude'])
    lon = float(location['longitude'])
    return lat, lon
 
#center_lon and center_lat JSC coordinates, center_lon = -95.093186
#center_lat = 29.552839
#latitude: 1 deg = 110.574km
#longitude: 1 deg = 111.320*cos(latitude)km
#radius of visibility = 2316.4km, when=> 40deg in sky, radius = 1774.5km  



# R is theoretically the visibility radius of the ISS, assuming a certain number of degrees above the horizon

R = 1774.5
center_lon = -95.093186
center_lat = 29.552839

# Create a daily dataframe for the ISS's trajectory
iss_map_df = pd.DataFrame([],
    columns=['latitude', 'longitude', 'local_time'])

while True:
    # Twilight API

    twilight_url = 'https://api.sunrise-sunset.org/json?lat={}&lng={}&formatted=0'.format(center_lat, center_lon)
    response = urllib.request.urlopen(twilight_url)
    result = json.loads(response.read())
    dic = result['results']

    end_time = dic['astronomical_twilight_begin']
    end_time = end_time.split('T')
    end_time = end_time[1].replace('+00:00', '')
    end_time = int(end_time.replace(':', ''))


    start_time = dic['astronomical_twilight_end']
    start_time = start_time.split('T')
    start_time = start_time[1].replace('+00:00', '')
    start_time = int(start_time.replace(':', ''))

    now = (int(datetime.now().strftime('%H%M%S')) + 70000)%235959 
    
    # Weather API
    
    weather_url= 'https://api.weather.gov/points/{},{}'.format(center_lat, center_lon)

    response0 = urllib.request.urlopen(weather_url)
    result0 = json.loads(response0.read())

    response1 = urllib.request.urlopen(result0['properties']['forecast'])
    result1 = json.loads(response1.read())

    weather = result1['properties']['periods'][0]['shortForecast']

# Parameters for running the ISS location API (clear weather and nightime in UTC)

    if now >= start_time and now <= end_time and weather == 'Clear' or weather == 'Mostly Clear':
        
        (lat, lon) = current_position('http://api.open-notify.org/iss-now.json')

        Rlat = (center_lat-lat) * 110.574
        Rlon = (center_lon-lon) * (111.320 * math.cos(lat*0.01745329))
        C = (math.sqrt(((Rlat) ** 2) + ((Rlon) ** 2)))
        
        if C <= R:
            print("It's here!", "lat:", lat, "lon:", lon, "Rlat:", Rlat, "Rlon:", Rlon, "C:", C)
            sleep(1800)
        else:
            print("nope", "lat:", lat, "lon:", lon, "Rlat:", Rlat, "Rlon:", Rlon, "C:", C)
            sleep(1)
    else:
        sleep(1)
    
