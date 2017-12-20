####################################################################
# SUMMARY OF CODE:                                                 #
# 1. Get all airport codes from a website                          #
# 2. Extract distance for each sources cities to all airports      #
#    and create panda dataset containing info                      #
# 3. Create a dataset containing each source city as rows and      #
#    a list of each airport locations for each incremental ranges  #
####################################################################

import pandas as pd
import requests
from bs4 import BeautifulSoup
import os.path

# Imports for dynamic content
from selenium import webdriver


# List of source airports
sources = ('nyc', 'mia', 'yul', 'los', 'rio', 'hkg', 'sin', 'dac', 'msq', 'syd', 'edi', 'cpt', 'auh', 'bjs', 'del')
# Incremental ranges
incremental_ranges = ['1-499', '500-999', '1000-1999', '2000-3999', '4000-5999', '6000-7999', '8000-9999',
                      '10000-11999', '12000-13999', '14000-15999', '16000-17999', '18000-99999']
AIRPORT_URL = "http://airportcod.es/"
DISTANCE_URL = "http://www.webflyer.com/travel/mileage_calculator/getmileage.php?city={0}&city={1}&city=&city=&city=&city=&bonus=0&bonus_use_min=0&class_bonus=0&class_bonus_use_min=0&promo_bonus=0&promo_bonus_use_min=0&min=0&min_type=m&ticket_price="

CSV_DISTANCES_FILENAME = "Distances_Between_Cities.csv"
CSV_INCREMENTAL_RANGES = "Incremental_Ranges_Data.csv"

###########
# STEP 1: #
###########


def get_airport_codes():
    codes = []
    try:
        # Start WebDriver and load the page
        driver = webdriver.Chrome()
        driver.get(AIRPORT_URL)

        # Wait 10 seconds for dynamic content to load
        driver.implicitly_wait(10)

        # Grab HTML
        html_data = driver.page_source
        driver.quit()

        # Parse Span tags and extract airport code
        soup = BeautifulSoup(html_data, 'html.parser')
        for link in soup.find_all('span'):
            if link is not None:
                airport = str(link).replace('<span>', '').replace('</span>', '')
                if len(airport) == 3:
                    codes.append(airport)
    except ValueError:
        print ("Error processing script")
    return codes

###########
# STEP 2: #
###########


# Get distances from a serialized csv file or get info from websites
def get_distances(airports, airport_codes):
    if os.path.exists(CSV_DISTANCES_FILENAME):
        df = pd.read_csv(CSV_DISTANCES_FILENAME, index_col=0)
        # Remove rows with 0s and serialize
        df = df.loc[~(df==0).all(axis=1)]
        df.to_csv(CSV_DISTANCES_FILENAME)
        return df
    # Create panda dataset containing the distances between each source city to each airports, initializing with zeros
    df = pd.DataFrame(index=airport_codes, columns=sources)
    df = df.fillna(0.0)
    try:
        for source_city in sources:
            for arrival_city in airports:
                if arrival_city != source_city:
                    response = requests.get(DISTANCE_URL.format(source_city, arrival_city))
                    soup = BeautifulSoup(response.text, 'lxml')
                    for span in soup.find_all('span'):
                        if 'km' in str(span) and 'row_odd_font' in str(span):
                            distance = str(span).replace('<span class="row_odd_font">', '').replace('</span>', '').strip()
                            distance = distance.replace('km', '').strip()
                            df.at[arrival_city, source_city] = float(distance)
                            break
    except ValueError as e:
        print ("Error processing script: ", e)

    # Serialize
    df.to_csv(CSV_DISTANCES_FILENAME)
    return df

###########
# STEP 3: #
###########


def get_cities_incrementalranges(distances_df):
    if os.path.exists(CSV_INCREMENTAL_RANGES):
        return pd.read_csv(CSV_INCREMENTAL_RANGES, index_col=0)
    # Convert to object so that we can insert list as a value
    df = pd.DataFrame(index=sources, columns=incremental_ranges).astype(object)

    for source in sources:
        for ranges in incremental_ranges:
            # Get all cities within range
            limits = ranges.split('-')
            # Add cities to dataframe
            df.at[source, ranges] = distances_df.loc[(distances_df[source] >= float(limits[0])) & (distances_df[source] <= float(limits[1]))][source].index.tolist()
    df.to_csv(CSV_INCREMENTAL_RANGES)
    return df


if __name__ == "__main__":
    # Scrape all airport codes
    airport_codes = get_airport_codes()
    # Get distances between each airports
    airport_distances = get_distances(airport_codes, airport_codes)
    # Get incremental ranges
    cities_incremental_ranges = get_cities_incrementalranges(airport_distances)