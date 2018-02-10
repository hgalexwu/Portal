import Scraper
import json
import datetime
import os
from datetime import date
import pandas as pd
import random
import argparse

# Range of Dates
DATE_RANGES = 120

# Folder for Data Scrape
SCRAPE_DIRECTORY = "Scrape_Data/"
# Serialized CSV files for DataFrame
CSV_INCREMENTAL_RANGES = "Incremental_Ranges_Data.csv"
# List of source airports
sources = ('nyc', 'mia', 'yul', 'los', 'rio', 'hkg', 'sin', 'dac', 'msq', 'syd', 'edi', 'cpt', 'auh', 'bjs', 'del')

# Directory folder the scraped data
directory = ""

# Maximum number of false attempts
MAX_ATTEMPTS = 2
# Number of consecutive days that we can skip
MAX_ATTEMPTS_SRAPE = 10

# Function returning the range of dates in /mm/dd/yy format
def get_range_dates(startdate, date_range):
    date_ranges = []
    for i in range(date_range):
        startdate += datetime.timedelta(days=1)
        date_ranges.append(date.strftime(startdate, '%m/%d/%y'))
    return date_ranges


def call_scrape_singlethreaded(source, cities):
    if len(cities) == 0 or cities[0] == '':
        return True
    for destination in cities:
        if source != destination or destination == '':
            results = []
            tries = 0
            for day in get_range_dates(date.today(), DATE_RANGES):
                scraped_data = Scraper.parse(source, destination, day, date.strftime(date.today(), '%m/%d/%y'))
                if scraped_data:
                    results += scraped_data
                    tries = 0
                else:
                    tries += 1
                    if tries >= MAX_ATTEMPTS_SRAPE:
                        print "ERROR: Exceeded Maximum Attempts"
                        return False
            file_name = SCRAPE_DIRECTORY + directory + '/%s-%s-%s-flight-results.json' % (date.strftime(date.today(), '%m%d%y'), source, destination)
            # Did not get the results, so return false
            if not results:
                return False
            with open(file_name, 'w') as fp:
                json.dump(results, fp, indent=4)
        # Case where the source = destination, we want to change cities
        else:
            return False
    return True


if __name__ == "__main__":

    # Make sure to use TOR so that we don't get blacklisted and stay anonymous
    # Use TOR port 9050
    # socks.setdefaultproxy(proxy_type=socks.PROXY_TYPE_SOCKS5, addr="127.0.0.1", port=9050)
    # socket.socket = socks.socksocket

    # Create a directory to store JSON if it doesn't exist
    directory = "Scrape_" + str(datetime.date.today())
    if not os.path.exists(SCRAPE_DIRECTORY + directory):
        os.makedirs(SCRAPE_DIRECTORY + directory)

    argparser = argparse.ArgumentParser()
    argparser.add_argument('source', help='Source airport code')
    args = argparser.parse_args()
    source_arg = args.source

    # Get incremental ranges dataframe
    source_incremental_range_cities = pd.read_csv(CSV_INCREMENTAL_RANGES, index_col=0)
    for source, ranges in source_incremental_range_cities.iterrows():
        if source_arg == source or source_arg == 'all':
            for cities_in_incremental_ranges in ranges.values:
                # Strip and create list bcz it was stored as a string
                cities_list = cities_in_incremental_ranges.replace("'", "").replace("[", "").replace("]", "").replace(" ", "").split(',')
                if source in cities_list:
                    cities_list.remove(source)
                # SINGLETHREADED VERSION
                # Repeat twice to get 2 cities or less
                for z in range(1): #range(min(2, len(cities_list))):
                    # Choose 1 or less random city
                    cities = random.sample(cities_list, min(1, len(cities_list)))
                    non_empty = call_scrape_singlethreaded(source, cities)
                    # Get a max of 2 tries
                    tries = 0
                    while not non_empty and tries < MAX_ATTEMPTS and len(cities_list) < 3:
                        cities = random.sample(cities_list, min(1, len(cities_list)))
                        non_empty = call_scrape_singlethreaded(source, cities)
                        tries += 1
                        # Get 5 tries
                        if tries > MAX_ATTEMPTS+2:
                            print ("ERROR: Exceeded Maximum Attempts in Main")
            # Get source airport prices
            call_scrape_singlethreaded(source, sources)
    print ("DONE WITH " + str(source_arg))

