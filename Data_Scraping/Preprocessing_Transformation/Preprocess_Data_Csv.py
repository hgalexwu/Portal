import pandas as pd
import os
import argparse
import json
from datetime import datetime
import re
import csv

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


def preprocess_data(in_path, out_path):
    airport_distances = pd.read_csv(CSV_DISTANCES_FILENAME, index_col=0)
    airport_info = json.load(open(AIRPORT_INFO_FILENAME))
    airport_aliases = json.load(open(AIRPORT_ALIASES_FILENAME))
    airport_status_mapping = {None: 0, "small": 1, "medium": 2, "large": 3}

    unrecognized_airports = []

    for dir in os.listdir(in_path):
        if dir.startswith('Scrape') and not dir.endswith('.txt'):
            # Create new directory to output
            if not os.path.exists(out_path + '/' + dir.replace("Scrape_", "")):
                os.makedirs(out_path + '/' + dir.replace("Scrape_", ""))
            for file in os.listdir(in_path + "/" + dir) :
                if file.endswith(".json"):
                    with (open(out_path + "/" + dir.replace("Scrape_", "") + "/" + file.replace(".json",".csv"), "wb")) as out_file:
                        csv_writer = csv.writer(out_file)
                        csv_writer.writerow(['arrival','distance','booking_date', 'city_status_destination',
                                                         'direct', 'continent_source', 'departure', 'stops', 'city_status_source',
                                                         'country_source', 'season', 'continent_destination', 'country_destination',
                                                         'airline', 'nb_flights_offered', 'international', 'travel_date',
                                                         'month_of_travel','days_until_departure','ticket_price'])
                        json_data = json.load(open(in_path + "/" + dir + "/" + file))
                        flight_data = []
                        for flight in json_data:
                            try:
                                # Check to see if its database of distances
                                if 'airportCode' not in flight['arrival']:
                                    arrival_airportcode = flight['arrival'].lower()
                                    departure_airportcode = flight['departure'].lower()
                                else:
                                    arrival_airportcode = flight['arrival']['airportCode'].lower()
                                    departure_airportcode = flight['departure']['airportCode'].lower()
                                if 'airline' in flight and flight['airline'] == "":
                                    flight['airline'] = None

                                if arrival_airportcode in airport_distances.index:
                                    # Convert price to int
                                    flight['ticket_price'] = float(flight['ticket_price'])
                                    # Calculate days until departure
                                    if 'days_until_departure' not in flight:
                                        flight['days_until_departure'] = calculate_date_difference(flight['booking_date'], flight['travel_date'])
                                    # Get Distances between Airports
                                    if 'distance' not in flight:
                                        if departure_airportcode not in sources:
                                            for aliases in airport_aliases:
                                                if aliases['alias'] == departure_airportcode:
                                                    if departure_airportcode == 'zvj':
                                                        departure_airportcode = 'auh'
                                                    flight['distance'] = airport_distances.at[arrival_airportcode, aliases['airportName']]
                                        else:
                                            flight['distance'] = airport_distances.at[arrival_airportcode, departure_airportcode]
                                    if 'city_status_source' not in flight or 'country_source' not in flight or 'continent_source' not in flight:
                                        for airport in airport_info:
                                            if airport['iata'].lower() == departure_airportcode:
                                                # Get City Statuses
                                                flight['city_status_source'] = airport_status_mapping[airport['size']]
                                                # Get Continents
                                                flight['continent_source'] = airport['continent']
                                                # Get Country
                                                flight['country_source'] = airport['iso']
                                            elif airport['iata'].lower() == arrival_airportcode:
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
                                        # Convert "Nonstop" and "x stops" values to ints
                                        if str(flight['stops']).lower() == 'nonstop':
                                            flight['stops'] = 0
                                        elif 'stop' in str(flight['stops']).lower():
                                            flight['stops'] = int(re.findall('\d+', flight['stops'])[0])

                                        # direct = 1, non-direct = 0
                                        if flight['stops'] == 0:
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

                                    # Change old format of certain files
                                    if 'airportCode' in flight['arrival']:
                                        flight['arrival'] = flight['arrival']['airportCode']
                                    if 'airportCode' in flight['departure']:
                                        flight['departure'] = flight['departure']['airportCode']

                                    #flight_data.append(flight)
                                    csv_writer.writerow([flight['arrival'],flight['distance'],flight['booking_date'], flight['city_status_destination'],
                                                         flight['direct'], flight['continent_source'], flight['departure'], flight['stops'], flight['city_status_source'],
                                                         flight['country_source'], flight['season'], flight['continent_destination'], flight['country_destination'],
                                                         flight['airline'], flight['nb_flights_offered'], flight['international'], flight['travel_date'],
                                                         flight['month_of_travel'],flight['days_until_departure'],flight['ticket_price']])
                                else:
                                    if arrival_airportcode not in unrecognized_airports:
                                        print (arrival_airportcode + " is not in the DB")
                                        unrecognized_airports.append(arrival_airportcode)

                            except Exception as e:
                                print ("Exception " + str(e) + ". For file: " + file)
                                continue
                        #with open(out_path + "/" + dir.replace("Scrape_", "") + "/" + file.replace(".json",".csv"), 'w') as outfile:
                            # json.dump(flight_data, outfile, indent=4)

# TRANSFORMATION??!!?!!?!



# TIME DELETED
# Round Trip Tag (should i remove?, yes because you need to include second date)
# Calculate days until return (with round trip, so delete)
# Calculate duration of stay (with round trip, so delete)


if __name__ == "__main__":

    argparser = argparse.ArgumentParser()
    argparser.add_argument('inpath', help='inpath')
    argparser.add_argument('outpath', help='outpath')
    args = argparser.parse_args()
    in_path = args.inpath
    out_path = args.outpath
    preprocess_data(in_path,out_path)