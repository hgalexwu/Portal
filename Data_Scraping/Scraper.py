import json
import requests
from lxml import html
from collections import OrderedDict
import argparse
import random
from fake_useragent import UserAgent
from bs4 import BeautifulSoup

# Number of tries to parse flight info
MAX_AMOUNT_TRIES = 2


# adapted from https://www.scrapehero.com/scrape-flight-schedules-and-prices-from-expedia/
def parse(source, destination, date, booking_date):
    for z in range(MAX_AMOUNT_TRIES):
        try:
            url = "https://www.expedia.com/Flights-Search?trip=oneway&leg1=from:{0},to:{1},departure:{2}TANYT&passengers=adults:1,children:0,seniors:0,infantinlap:Y&options=cabinclass%3Aeconomy&mode=search&origref=www.expedia.com".format(
                  source, destination, date)
            ua = UserAgent()
            header = {
                'User-Agent': str(ua.random)
            }
            response = requests.get(url, headers=header)
            parser = html.fromstring(response.text)
            json_data_xpath = parser.xpath("//script[@id='cachedResultsJson']//text()")
            if len(json_data_xpath) < 1:
                print "JSON_DATA_XPATH of length 0 for " + str(source) + " to " + str(destination) + " on " + str(date)
                soup = BeautifulSoup(parser, 'html.parser')
                raise ValueError
            raw_json = json.loads(json_data_xpath[0])
            flight_data = json.loads(raw_json["content"])

            flight_info = OrderedDict()
            lists = []
            for i in flight_data['legs'].keys():
                departure = flight_data['legs'][i]['departureLocation']
                arrival = flight_data['legs'][i]['arrivalLocation']
                total_distance = str(flight_data['legs'][i]["formattedDistance"]) + ' miles'

                exact_price = flight_data['legs'][i]['price']['totalPriceAsDecimal']
                airline_name = flight_data['legs'][i]['carrierSummary']['airlineName']
                no_of_stops = flight_data['legs'][i]["stops"]
                flight_duration = flight_data['legs'][i]['duration']
                flight_hour = flight_duration['hours']
                flight_minutes = flight_duration['minutes']
                flight_days = flight_duration['numOfDays']
                if no_of_stops == 0:
                    stop = "Nonstop"
                else:
                    stop = str(no_of_stops) + ' Stops'

                total_flight_duration = "{0} days {1} hours {2} minutes".format(flight_days, flight_hour,
                                                                                flight_minutes)

                formatted_price = "{0:.2f}".format(exact_price)
                if flight_data['legs'][i]['timeline'] is not None and len(flight_data['legs'][i]['timeline']) > 0:
                    carrier = flight_data['legs'][i]['timeline'][0]['carrier']
                    plane = carrier['plane']
                    plane_code = carrier['planeCode']
                else:
                    print ('No Timeline Data')
                    raise ValueError

                if not airline_name:
                    airline_name = carrier['operatedBy']
                carrier_operation = carrier['operatedBy']

                # Removed timings because it is not necessary information
                # timings = []
                # for timeline in flight_data['legs'][i]['timeline']:
                #     if 'departureAirport' in timeline.keys():
                #         departure_airport = timeline['departureAirport']['longName']
                #         departure_time = timeline['departureTime']['time']
                #         arrival_airport = timeline['arrivalAirport']['longName']
                #         arrival_time = timeline['arrivalTime']['time']
                #         flight_timing = {
                #             'departure_airport': departure_airport,
                #             'departure_time': departure_time,
                #             'arrival_airport': arrival_airport,
                #             'arrival_time': arrival_time
                #         }
                #         timings.append(flight_timing)

                flight_info = {'stops': stop,
                               'total_distance': total_distance,
                               'departure': departure,
                               'arrival': arrival,
                               'ticket_price': formatted_price,
                               'flight_duration': total_flight_duration,
                               'airline': airline_name,
                               'carrier_operatedby': carrier_operation,
                               'plane': plane,
                               # 'timings': timings,
                               'plane_code': plane_code,
                               'travel_date': date,
                               'booking_date': booking_date
                               }
                if flight_info['airline'] != "":
                    lists.append(flight_info)
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
        except ValueError:
            # print ("Retrying...")
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
