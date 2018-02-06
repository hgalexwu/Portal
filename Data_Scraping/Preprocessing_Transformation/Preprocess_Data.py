import pandas as pd
import os
import argparse
import json
from datetime import datetime


CSV_DISTANCES_FILENAME = "../Distances_Between_Cities.csv"
AIRPORT_INFO_FILENAME = "./airports.json"
AIRPORT_ALIASES_FILENAME = "./airport_aliases.json"
DIRECTORY_PREPROCESSED_FILES = "./"

sources = ('nyc', 'mia', 'yul', 'los', 'rio', 'hkg', 'sin', 'dac', 'msq', 'syd', 'edi', 'cpt', 'auh', 'bjs', 'del')


def calculate_date_difference(booking_date, travel_date):
    date_format = "%m/%d/%Y"
    year_travel = '20' + travel_date[-2:]
    year_booking = '20' + booking_date[-2:]
    d0 = datetime.strptime(travel_date[:-2]+year_travel, date_format)
    d1 = datetime.strptime(booking_date[:-2]+year_booking, date_format)
    if "days" in str(d0-d1):
        return int(str((d0-d1)).split("days")[0])
    else:
        return int(str((d0-d1)).split("day")[0])


def preprocess_data(path):
    airport_distances = pd.read_csv(CSV_DISTANCES_FILENAME, index_col=0)
    airport_info = json.load(open(AIRPORT_INFO_FILENAME))
    airport_aliases = json.load(open(AIRPORT_ALIASES_FILENAME))
    airport_status_mapping = {None : "0", "small": "1", "medium": "2", "large": "3"}

    for dir in os.listdir(path):
        if dir.startswith('Scrape') and not dir.endswith('.txt'):
            for file in os.listdir(path + "/" + dir) :
                if file.endswith(".json"):
                    json_data = json.load(open(path + "/" + dir + "/" + file))
                    for flight in json_data:
                        # Check to see if its database of distances
                        if flight['arrival']['airportCode'].lower() in airport_distances.index:
                            # Calculate days until departure
                            if 'days_until_departure' not in flight:
                                flight['days_until_departure'] = calculate_date_difference(flight['booking_date'], flight['travel_date'])
                            # Get Distances between Airports
                            if 'distance' not in flight:
                                if (flight['departure']['airportCode'].lower() not in sources):
                                    for aliases in airport_aliases:
                                        if aliases['alias'] == flight['departure']['airportCode'].lower():
                                            flight['distance'] = airport_distances.at[flight['arrival']['airportCode'].lower(),aliases['airportName']]
                                else:
                                    flight['distance'] = airport_distances.at[flight['arrival']['airportCode'].lower(), flight['departure']['airportCode'].lower()]
                            if 'city_status_source' not in flight or 'country_source' not in flight or 'continent_source' not in flight:
                                for airport in airport_info:
                                    if airport['iata'] == flight['departure']['airportCode']:
                                        # Get City Statuses
                                        flight['city_status_source'] = airport_status_mapping[airport['size']]
                                        # Get Continents
                                        flight['continent_source'] = airport['continent']
                                        # Get Country
                                        flight['country_source'] = airport['iso']
                                    elif airport['iata'] == flight['arrival']['airportCode']:
                                        # Get City Statuses
                                        flight['city_status_destination'] = airport_status_mapping[airport['size']]
                                        # Get Continents
                                        flight['continent_destination'] = airport['continent']
                                        # Get Country
                                        flight['country_destination'] = airport['iso']
                            # International Tag
                            if 'international' not in flight:
                                if flight['country_source'] == flight['country_destination']:
                                    # International flight = 1, Domestic = 0
                                    flight['international'] = 0
                                else:
                                    flight['international'] = 1
                            # Direct Tag
                            if 'direct' not in flight:
                                # direct = 1, non-direct = 0
                                if flight['stops'] == 'Nonstop':
                                    flight['direct'] = 1
                                else:
                                    flight['direct'] = 0
                            # Separate Month of Travel
                            if 'month_of_travel' not in flight:
                                flight['month_of_travel'] = int(flight['travel_date'][:2])
                            # Separate Season
                            if 'season' not in flight:
                                # FROM: http://www.reidsguides.com/t_pl/air_timing.html
                                # High Season (2) => December 15th to January 6th.
                                if int(flight['travel_date'][:2]) == 12 and int(flight['travel_date'][3:5]) >= 15:
                                    flight['season'] = 2
                                elif int(flight['travel_date'][:2]) == 1 and int(flight['travel_date'][3:5]) <= 6:
                                    flight['season'] = 2
                                # High Season => June 15th to Aug 31
                                elif int(int(flight['travel_date'][:2]) == 8 or int(flight['travel_date'][:2]) == 7 or (int(flight['travel_date'][:2]) == 6 and int(flight['travel_date'][3:5]) >= 15)):
                                    flight['season'] = 2
                                # Shoulder seasons: April 1 to Jun 14
                                elif (int(flight['travel_date'][:2]) == 4 or int(flight['travel_date'][:2]) == 5) or (int(flight['travel_date'][:2]) == 6 and int(flight['travel_date'][3:5]) <= 14):
                                    flight['season'] = 1
                                # Shoulder seasons: Sept 1 to Oct 31
                                elif (int(flight['travel_date'][:2]) == 9 or int(flight['travel_date'][:2]) == 10):
                                    flight['season'] = 1
                                # Low Season
                                else:
                                    flight['season'] = 0

                        # with open(path + "/" + dir + "/" + file, 'w') as outfile:
                        #     json.dump(json_data, outfile)

                        # Add to MongoDB
                        # Check if it exists, if it doesn't add.
                        else:
                            print (flight['arrival']['airportCode'] + " is not in the DB")



# TRANSFORMATION??!!?!!?!



# TIME DELETED
# Round Trip Tag (should i remove?, yes because you need to include second date)
# Calculate days until return (with round trip, so delete)
# Calculate duration of stay (with round trip, so delete)


if __name__ == "__main__":

    argparser = argparse.ArgumentParser()
    argparser.add_argument('path', help='Path')
    args = argparser.parse_args()
    path = args.path

    preprocess_data(path)