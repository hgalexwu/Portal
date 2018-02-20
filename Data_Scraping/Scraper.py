import json
import requests
from lxml import html
from collections import OrderedDict
import argparse
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from bs4 import BeautifulSoup

# Number of tries to parse flight info
MAX_AMOUNT_TRIES = 1


def parse_with_selenium(url, date, booking_date):
    # Start WebDriver and load the page
    # Options below added for selenium in AWS to work
    options = webdriver.ChromeOptions()
    options.add_argument('--disable-extensions')
    options.add_argument('--headless')
    options.add_argument('--disable-gpu')
    options.add_argument('--no-sandbox')
    driver = webdriver.Chrome(chrome_options=options)
    driver.get(url)
    # Wait 10 seconds for dynamic content to load
    WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.XPATH, "//*[@id='flightModuleList']")))
    # Grab HTML
    html_data = driver.page_source.encode('utf-8').decode('string_escape')
    driver.quit()
    soup = BeautifulSoup(html_data, 'lxml')
    flex_content = soup.find("ul", {"id": "flightModuleList"}).find_all("li", {"class": "flight-module segment offer-listing"})
    flight_info = OrderedDict()
    lists = []
    for fc in flex_content:
        total_flight_duration = fc.find("span", {"data-test-id": "duration"}).get_text().replace("\n", "").strip()
        airline_name = fc.find("span", {"data-test-id": "airline-name"}).get_text().replace("\n", "").strip()
        departure = fc.find("div", {"data-test-id": "flight-info"}).get_text().replace("Departure airport:","").replace("Arrival airport:", "").replace("\n", "").split("-")[0].strip()
        arrival = fc.find("div", {"data-test-id": "flight-info"}).get_text().replace("Departure airport:","").replace("Arrival airport:", "").replace("\n", "").split("-")[-1].strip()
        exact_price = float(fc.find("span", {"data-test-id": "listing-price-dollars"}).get_text().replace("$","").replace(",", ""))
        no_of_stops = fc.find("span", {"class": "number-stops"}).get_text().replace("\n", "").strip().replace("(","").replace(")","")

        #total_flight_duration = fc.find("div", {"data-test-id": "duration"}).get_text().replace("\n", "").strip()
        #airline_name = fc.find("div", {"data-test-id": "airline-name"}).get_text().replace("\n", "").strip()
        #departure = fc.find("div", {"data-test-id": "airports"}).get_text().split(" - ")[0]
        #arrival = fc.find("div", {"data-test-id": "airports"}).get_text().split(" - ")[1]
        #exact_price = float(fc.find("span", {"class": "dollars price-emphasis"}).get_text().replace("$","").replace(",", ""))
        #no_of_stops = fc.find("div", {"class": "primary stops-emphasis"}).get_text().replace("\n", "").strip()

        ##total_flight_duration = "{0} days {1} hours {2} minutes".format(flight_days, flight_hour, flight_minutes)
        formatted_price = "{0:.2f}".format(exact_price)
        flight_info = {'stops': no_of_stops,
                       'departure': departure,
                       'arrival': arrival,
                       'ticket_price': formatted_price,
                       'flight_duration': total_flight_duration,
                       'airline': airline_name,
                       'travel_date': date,
                       'booking_date': booking_date
                       }
        lists.append(flight_info)
    return lists


# adapted from https://www.scrapehero.com/scrape-flight-schedules-and-prices-from-expedia/
def parse(source, destination, date, booking_date):
    for z in range(MAX_AMOUNT_TRIES):
        try:
            url = "https://www.expedia.com/Flights-Search?trip=oneway&leg1=from:{0},to:{1},departure:{2}TANYT&passengers=children:0,adults:1,seniors:0,infantinlap:Y&mode=search".format(source, destination, date)
            headers = {'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/42.0.2311.90 Safari/537.36'}

            response = requests.get(url, headers=headers)
            parser = html.fromstring(response.text)
            json_data_xpath = parser.xpath("//script[@id='cachedResultsJson']//text()")

            # Parse response using Selenium
            if len(json_data_xpath) < 1:
            #  print "Try Number " + str(z) + ": JSON_DATA_XPATH of length 0 for " + str(source) + " to " + str(destination) + " on " + str(date) + " with Status Code " + str(response.status_code)
                if response.status_code == 200:
                    lists = parse_with_selenium(url, date, booking_date)
                else:
                    print ("Error: Status code not 200")
                    print (response.headers)
                    raise ValueError
            else:
                # Parse the response the normal way
                raw_json = json.loads(json_data_xpath[0])
                flight_data = json.loads(raw_json["content"])

                flight_info = OrderedDict()
                lists = []
                for i in flight_data['legs'].keys():
                    departure = flight_data['legs'][i]['departureLocation']['airportCode']
                    arrival = flight_data['legs'][i]['arrivalLocation']['airportCode']
                    exact_price = flight_data['legs'][i]['price']['totalPriceAsDecimal']
                    airline_name = flight_data['legs'][i]['carrierSummary']['airlineName']
                    no_of_stops = flight_data['legs'][i]["stops"]
                    flight_duration = flight_data['legs'][i]['duration']
                    flight_hour = flight_duration['hours']
                    flight_minutes = flight_duration['minutes']
                    flight_days = flight_duration['numOfDays']

                    total_flight_duration = "{0} days {1} hours {2} minutes".format(flight_days, flight_hour, flight_minutes)

                    formatted_price = "{0:.2f}".format(exact_price)
                    if flight_data['legs'][i]['timeline'] is not None and len(flight_data['legs'][i]['timeline']) > 0:
                        carrier = flight_data['legs'][i]['timeline'][0]['carrier']
                    else:
                        print ('No Timeline Data')
                        raise ValueError

                    if not airline_name:
                        airline_name = carrier['operatedBy']

                    flight_info = {'stops': no_of_stops,
                                   'departure': departure,
                                   'arrival': arrival,
                                   'ticket_price': formatted_price,
                                   'flight_duration': total_flight_duration,
                                   'airline': airline_name,
                                   'travel_date': date,
                                   'booking_date': booking_date
                                   }
                    lists.append(flight_info)
            # Parse using selenium if we get an empty list
            if not lists:
                lists = parse_with_selenium(url, date, booking_date)

            sortedlist = sorted(lists, key=lambda k: (k['airline'], k['stops'], k['ticket_price'], k['flight_duration']), reverse=False)

            cheapest_flights = []
            existing_flights = {}
            # Logic to retain only the cheapest flight for each airline
            for flights in sortedlist:
                # Store cheapest flight of each airline and keep at least one nonstop flight
                if flights['airline'] not in existing_flights or (existing_flights[flights['airline']] != 'Nonstop' and flights['stops'] == 'Nonstop'):
                    existing_flights[flights['airline']] = flights['stops']
                    flights['nb_flights_offered'] = len(sortedlist)
                    # Add number of offered flights, to determine city status
                    cheapest_flights.append(flights)

            if not cheapest_flights:
                print (" Data scrape didn't work for:", source, destination, date, booking_date)
                raise ValueError
            return cheapest_flights
        except ValueError as e:
            print ("Error: " + str(e) + ". Retrying...")
            continue
        except Exception as e:
            print ("Error: " + str(e) + ". Retrying...")
            continue
        return []
        #return {" Error": "failed to process the page for: " + source + ", " + destination + ", " + date + ", " + booking_date}
 

if __name__ == "__main__":
    argparser = argparse.ArgumentParser()
    argparser.add_argument('source', help='Source airport code')
    argparser.add_argument('destination', help='Destination airport code')
    argparser.add_argument('date', help='MM/DD/YYYY')
    argparser.add_argument('booking_date', help='MM/DD/YYYY')

    args = argparser.parse_args()
    source = args.source
    destination = args.destination
    date = args.date
    booking_date = args.booking_date
    print ("Fetching flight details")
    scraped_data = parse(source, destination, date, booking_date)
    print ("Writing data to output file")
    with open('%s-%s-%s-flight-results.json' % (date.replace('/', ''), source, destination), 'w') as fp:
        json.dump(scraped_data, fp, indent=4)
