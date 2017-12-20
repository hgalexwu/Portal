import Scraper
import json
import datetime
import os
from datetime import date
import pandas as pd
import random
import multiprocessing

# Range of Dates
DATE_RANGES = 250

# Folder for Data Scrape
SCRAPE_DIRECTORY = "Scrape_Data/"
# Serialized CSV files for DataFrame
CSV_INCREMENTAL_RANGES = "Incremental_Ranges_Data.csv"
# List of source airports
sources = ('nyc', 'mia', 'yul', 'los', 'rio', 'hkg', 'sin', 'dac', 'msq', 'syd', 'edi', 'cpt', 'auh', 'bjs', 'del')

# Directory folder the scraped data
directory = ""


# Function returning the range of dates in /mm/dd/yy format
def get_range_dates(startdate, date_range):
    date_ranges = []
    for i in range(date_range):
        startdate += datetime.timedelta(days=1)
        date_ranges.append(date.strftime(startdate, '%m/%d/%y'))
    return date_ranges


def call_scrape(source, cities):
    for destination in cities:
        if source != destination:
            results = []
            for day in get_range_dates(date.today(), DATE_RANGES):
                scraped_data = Scraper.parse(source, destination, day, date.strftime(date.today(), '%m/%d/%y'))
                # 2 tries to get data
                for i in range(2):
                    if len(scraped_data) > 0:
                        results.append(scraped_data)
                        break
            file_name = SCRAPE_DIRECTORY + directory + '/%s-%s-%s-flight-results.json' % (date.strftime(date.today(), '%m%d%y'), source, destination)
            # print ("Writing data to output file: ", file_name)
            with open(file_name, 'w') as fp:
                json.dump(results, fp, indent=4)


def call_scrape_multithreaded(i, nb_tasks, source_incremental_range_cities):
    print "Process " + str(i) + " started..."
    for source, ranges in source_incremental_range_cities.iloc[i*nb_tasks:(i+1)*nb_tasks].iterrows():
        for cities_in_incremental_ranges in ranges.values:
            # Strip and create list bcz it was stored as a string
            cities_list = cities_in_incremental_ranges.replace("'", "").replace("[", "").replace("]", "").replace(" ", "").split(',')
            # Choose 2 or less random cities
            cities = random.sample(cities_list, min(2, len(cities_list)))
            call_scrape(source, cities)
        # Choose 2 cities from the source cities
        call_scrape(source, random.sample(sources, min(2, len(sources))))
        print ("Process " + str(i) + " finished writing data for source city: " + source)
    print "Process " + str(i) + " finished all tasks."


if __name__ == "__main__":
    # Create a directory to store JSON if it doesn't exist
    directory = "Scrape_" + str(datetime.date.today())
    if not os.path.exists(SCRAPE_DIRECTORY + directory):
        os.makedirs(SCRAPE_DIRECTORY + directory)

    # Get distances between airports dataframe
    source_incremental_range_cities = pd.read_csv(CSV_INCREMENTAL_RANGES, index_col=0)
    # Create processes to run 5 source cities to run in parallel to compute faster
    nb_tasks = 5
    for i in range(1,3):
        p = multiprocessing.Process(target=call_scrape_multithreaded, args=(i, nb_tasks, source_incremental_range_cities))
        p.start()
    call_scrape_multithreaded(0, nb_tasks, source_incremental_range_cities)