import Scraper
import json
import datetime
import os
from datetime import date
import pandas as pd
import random
from lxml import html
import grequests
import requests
import multiprocessing as mp

# Range of Dates
DATE_RANGES = 225

# Folder for Data Scrape
SCRAPE_DIRECTORY = "Scrape_Data/"
# Serialized CSV files for DataFrame
CSV_INCREMENTAL_RANGES = "Incremental_Ranges_Data.csv"
# List of source airports
sources = ('nyc', 'mia', 'yul', 'los', 'rio', 'hkg', 'sin', 'dac', 'msq', 'syd', 'edi', 'cpt', 'auh', 'bjs', 'del')

# Directory folder the scraped data
directory = ""

# Maximum number of asynchronous http requests
MAX_ASYNC_SIZE = 25


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
                # 2 tries to get data
                for i in range(2):
                    scraped_data = Scraper.parse("", source, destination, day, date.strftime(date.today(), '%m/%d/%y'))
                    if len(scraped_data) > 0:
                        results.append(scraped_data)
                        break
            file_name = SCRAPE_DIRECTORY + directory + '/%s-%s-%s-flight-results.json' % (date.strftime(date.today(), '%m%d%y'), source, destination)
            # print ("Writing data to output file: ", file_name)
            with open(file_name, 'w') as fp:
                json.dump(results, fp, indent=4)


def call_scrape_multithreaded(source, cities):
    for destination in cities:
        if source != destination:
            results = []
            pool = mp.Pool(processes=4)
            scraped_data = pool.map(Scraper.parse, [(source, destination, day, date.strftime(date.today(), '%m/%d/%y')) for day in get_range_dates(date.today(), DATE_RANGES)])
            for idx, day in enumerate(get_range_dates(date.today(), DATE_RANGES)):
                # 2 tries to get data
                for i in range(2):
                    if len(scraped_data[idx]) > 0:
                        results.append(scraped_data[idx])
                        break
                    else:
                        scraped_data[idx] = Scraper.parse(source, destination, day, date.strftime(date.today(), '%m/%d/%y'))
            file_name = SCRAPE_DIRECTORY + directory + '/%s-%s-%s-flight-results.json' % (date.strftime(date.today(), '%m%d%y'), source, destination)
            # print ("Writing data to output file: ", file_name)
            with open(file_name, 'w') as fp:
                json.dump(results, fp, indent=4)
            pool.close()
            pool.join()


# Goal is to async each http requests and when one is done, process it using scraper.
def call_scrape_async(source, cities):
    for destination in cities:
        if source != destination:
            results = []
            urls = []
            for day in get_range_dates(date.today(), DATE_RANGES):
                urls.append("https://www.expedia.com/Flights-Search?trip=oneway&leg1=from:{0},to:{1},departure:{2}TANYT&passengers=adults:1,children:0,seniors:0,infantinlap:Y&options=cabinclass%3Aeconomy&mode=search&origref=www.expedia.com".format(
                source, destination, day))
            unsent_requests = (grequests.get(url) for url in urls)
            responses = grequests.map(unsent_requests, size=20)
            for idx, day in enumerate(get_range_dates(date.today(), DATE_RANGES)):
                parser = html.fromstring(responses[idx].text)
                results.append(Scraper.parse("", source, destination, day, date.strftime(date.today(), '%m/%d/%y'), parser.xpath("//script[@id='cachedResultsJson']//text()")))
            file_name = SCRAPE_DIRECTORY + directory + '/%s-%s-%s-flight-results.json' % (date.strftime(date.today(), '%m%d%y'), source, destination)
            if not results:
                return False
            with open(file_name, 'w') as fp:
                json.dump(results, fp, indent=4)
        # Case where the source = destination, we want to change cities
        else:
            return False
    return True


def call_scrape_singlethreaded(source, cities):
    for destination in cities:
        if source != destination:
            results = []
            for day in get_range_dates(date.today(), DATE_RANGES):
                scraped_data = Scraper.parse("", source, destination, day, date.strftime(date.today(), '%m/%d/%y'))
                results += scraped_data

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


def get_result(result, results):
    results += result


def call_scrape_async_multithreaded(source, cities):
    for destination in cities:
        if source != destination:
            results = []
            pool = mp.Pool(processes=2)
            for day in get_range_dates(date.today(), DATE_RANGES):
                callback = lambda result: get_result(result, results)
                pool.apply_async(Scraper.parse, args=("", source, destination, day, date.strftime(date.today(), '%m/%d/%y')), callback=callback)
            file_name = SCRAPE_DIRECTORY + directory + '/%s-%s-%s-flight-results.json' % (date.strftime(date.today(), '%m%d%y'), source, destination)
            pool.close()
            pool.join()
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
    # Create a directory to store JSON if it doesn't exist
    directory = "Scrape_" + str(datetime.date.today())
    if not os.path.exists(SCRAPE_DIRECTORY + directory):
        os.makedirs(SCRAPE_DIRECTORY + directory)

    # Get incremental ranges dataframe
    source_incremental_range_cities = pd.read_csv(CSV_INCREMENTAL_RANGES, index_col=0)
    for source, ranges in source_incremental_range_cities.iterrows():
        for cities_in_incremental_ranges in ranges.values:
            # Strip and create list bcz it was stored as a string
            cities_list = cities_in_incremental_ranges.replace("'", "").replace("[", "").replace("]", "").replace(" ", "").split(',')

        # MULTITHREADED VERSION
        #     # Choose 2 or less random city
        #     cities = random.sample(cities_list, min(2, len(cities_list)))
        #     call_scrape_multithreaded(source, cities)
        # # Choose 2 cities from the source cities
        # call_scrape_multithreaded(source, random.sample(sources, min(2, len(sources))))

        # SINGLETHREADED VERSION
            # Choose 1 or less random city
            cities = random.sample(cities_list, min(1, len(cities_list)))
            non_empty = call_scrape_singlethreaded(source, cities)
            while not non_empty:
                cities = random.sample(cities_list, min(1, len(cities_list)))
                non_empty = call_scrape_singlethreaded(source, cities)
        # Choose 2 cities from the source cities
        call_scrape_singlethreaded(source, random.sample(sources, min(2, len(sources))))
