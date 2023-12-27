import requests
from requests.auth import HTTPBasicAuth
import datetime
from geopy.geocoders import Photon
import pandas as pd

##### USING THE FREE VERSION OF THIS API #####

#This expands the dataframe in the console in the console
pd.set_option('display.expand_frame_repr', False)

#This is the beginning of the day
#No slash on the Z because this is going to be start of the day to time right now
beginningTime = datetime.time.min.isoformat()
beginningDate = datetime.date.today()
beginningOfDay = str(beginningDate) + "T" + beginningTime + "Z"

#This is the current time which be the end of our search
#We will be searching through the start to the end of the day
timeNow = datetime.datetime.now().isoformat()
time =  beginningOfDay + "--" + timeNow + "Z:PT1H/"

#Interacting with API
parameters = "t_2m:F,wind_speed_10m:ms/"
tucson = "32.1543,-110.871"
phoenix = "33.4489,-112.0771"
flagstaff = "35.198284,-111.651299"
format = "/json"
api_url_tucson = "http://api.meteomatics.com/"+ time + parameters + tucson + format
api_url_phoenix = "http://api.meteomatics.com/"+ time + parameters + phoenix + format
api_url_flagstaff = "http://api.meteomatics.com/"+ time + parameters + flagstaff + format

#Logging into the API
username = ''
password = ''
authutencation = HTTPBasicAuth(username, password)
responseTucson = requests.get(api_url_tucson, auth=authutencation)
responsePhoenix = requests.get(api_url_phoenix, auth=authutencation)
responseFlagstaff = requests.get(api_url_flagstaff, auth=authutencation)


#This will grab the temperature values and wind values
#This will also interact with location and put it all into a data frame
def weatherDataFrame(data, coords):
    tempList = []
    windList = []
    
    #With the given coords we will find the country, city, and state
    locationInfo = []
    geolocator = Photon(user_agent="measurements")
    location = geolocator.reverse(coords)
    address = location.raw  
    locationInfo.append(address['properties'])

    #Loop through temperature and wind(m/s)
    for item in data.json()['data']:
        if item['parameter'] == 't_2m:F':
            for temp in item['coordinates']:
                for tempDates in temp['dates']:
                    tempList.append(tempDates)
        if item['parameter'] == 'wind_speed_10m:ms':
            for wind in item['coordinates']:
                for windDates in wind['dates']:
                    windList.append(windDates)
    
    #Makes a temperature dataframe and a wind dataframe
    tempDataFrame = pd.DataFrame(tempList)
    windDataFrame = pd.DataFrame(windList)

    #Renames date and value in the temperature data frame
    temp_frame = tempDataFrame.rename(columns={'date': 'Date & Time',
                                                'value': 'Degrees(F)'},
                                    inplace=False)

    #Renames date and value in the wind data frame
    wind_frame = windDataFrame.rename(columns={'date': 'Date & Time',
                                                'value': 'Wind(m/s)'},
                                    inplace=False)

    #merges the 2 data frames together by "Date & Time" as they are the same
    dataFrameMerge = pd.merge(temp_frame, wind_frame, on='Date & Time')
    
    #Making the city,state, and country data table
    locationInfoDataFrame = pd.DataFrame(locationInfo)
 
    #If the coords are the same as tucson then drop certain values   
    if coords == tucson:
        locationInfoDataFrame.drop(['osm_type', 'osm_id', 'extent', 'osm_key', 'countrycode', 'osm_value', 'name', 'county', 'type', 'postcode'], axis=1, inplace=True)

    #If the coords are the same as phoenix then drop certain values      
    if coords == phoenix:
        locationInfoDataFrame.drop(['osm_type', 'osm_id', 'housenumber', 'osm_key', 'countrycode', 'osm_value', 'name', 'county', 'type', 'postcode', 'street'], axis=1, inplace=True)
    
    #If the coords are the same as flagstaff then drop certain values  
    if coords == flagstaff:
        locationInfoDataFrame.drop(['osm_type', 'osm_id', 'extent', 'osm_key', 'countrycode', 'osm_value', 'name', 'county', 'type', 'postcode', 'locality'], axis=1, inplace=True)
        
    #This will rename the location Dataframe, Capitalizing country, city, and state
    renamedLocationDataFrame = locationInfoDataFrame.rename(columns={'country': 'Country',
                                                                    'city': 'City',
                                                                    'state': 'State'},
                                                            inplace=False)

    #This will fill all NaN's from Country, City, and State with the same value as they are all the same
    dataFrame = dataFrameMerge.join(renamedLocationDataFrame).fillna({'Country': address['properties']['country'],
                                                                      'City': address['properties']['city'],
                                                                      'State': address['properties']['state']})
    #Print out this dataframe
    print(dataFrame)


#Tucson weather
weatherDataFrame(responseTucson, tucson)
print("-----------------------------------------------------------")
#Phoenix weather
weatherDataFrame(responsePhoenix, phoenix)
print("-----------------------------------------------------------")
#Flagstaff weather
weatherDataFrame(responseFlagstaff, flagstaff)
    