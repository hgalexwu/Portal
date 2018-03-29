# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.shortcuts import render

# Create your views here.
from django.http import HttpResponse, JsonResponse
from django.views.decorators.csrf import csrf_exempt
# from django.views.generic import View

import json
from oauth2client.client import GoogleCredentials
import googleapiclient.discovery
project_name = "astute-backup-134320"
model_name = "Portal_First_Estimators_Model"
version_name = "a"
from datetime import date
import datetime


import requests
from bs4 import BeautifulSoup
AIRPORT_INFO_FILENAME = "./airports.json"
AIRPORT_ALIASES_FILENAME = "./airport_aliases.json"
DISTANCE_URL = "http://www.webflyer.com/travel/mileage_calculator/getmileage.php?city={0}&city={1}&city=&city=&city=&city=&bonus=0&bonus_use_min=0&class_bonus=0&class_bonus_use_min=0&promo_bonus=0&promo_bonus_use_min=0&min=0&min_type=m&ticket_price="

# Function returning the range of dates in /mm/dd/yy format
def get_range_dates(startdate, date_range):
	date_ranges = []
	date_ranges.append(date.strftime(startdate, '%m/%d/%y'))
	for i in range(date_range-1):
		startdate += datetime.timedelta(days=1)
		date_ranges.append(date.strftime(startdate, '%m/%d/%y'))
	return date_ranges


def calculate_date_difference(booking_date, travel_date):
	date_format = "%Y-%m-%d"
	d0 = datetime.datetime.strptime(travel_date, date_format)
	d1 = datetime.datetime.strptime(booking_date, date_format)
	if "days" in str(d0-d1):
		return int(str((d0-d1)).split("days")[0])
	else:
		return int(str((d0-d1)).split("day")[0])

def calculate_date_difference_diff(booking_date, travel_date):
	date_format = "%m/%d/%y"
	d0 = datetime.datetime.strptime(travel_date, date_format)
	d1 = datetime.datetime.strptime(booking_date, date_format)
	if "days" in str(d0-d1):
		return int(str((d0-d1)).split("days")[0])
	else:
		return int(str((d0-d1)).split("day")[0])


def predict_json(project, model, instances, version=None):
	"""Send json data to a deployed model for prediction.

	Args:
		project (str): project where the Cloud ML Engine Model is deployed.
		model (str): model name.
		instances ([Mapping[str: Any]]): Keys should be the names of Tensors
			your deployed model expects as inputs. Values should be datatypes
			convertible to Tensors, or (potentially nested) lists of datatypes
			convertible to tensors.
		version: str, version of the model to target.
	Returns:
		Mapping[str: any]: dictionary of prediction results defined by the
			model.
	"""
	# Create the ML Engine service object.
	# To authenticate set the environment variable
	# GOOGLE_APPLICATION_CREDENTIALS=<path_to_service_account_file>
	service = googleapiclient.discovery.build('ml', 'v1')
	name = 'projects/{}/models/{}'.format(project, model)

	if version is not None:
		name += '/versions/{}'.format(version)
	response = service.projects().predict(
		name=name,
		body=instances
	).execute()
	if 'error' in response:
		raise RuntimeError(response['error'])

	return response['predictions']

def get_distance(flyingFrom,flyingTo):
	return 0

def get_flight_input(flyingFrom, flyingTo, dateFrom, dateTo):
	print (flyingFrom,flyingTo, dateFrom, dateTo, calculate_date_difference(str(date.today()),dateFrom))
	date_ranges = get_range_dates(date.today(),calculate_date_difference(str(date.today()),dateFrom))
	
	# airport files
	airport_info = json.load(open(AIRPORT_INFO_FILENAME))
	airport_aliases = json.load(open(AIRPORT_ALIASES_FILENAME))
	airport_status_mapping = {None: 0, "small": 1, "medium": 2, "large": 3}


	prediction_input = {"instances":[]}
	travel_date = str(datetime.datetime.strptime(dateFrom, "%Y-%m-%d")).split(" ")[0]
	travel_date = travel_date[5:7] + "/" + travel_date[8:10] + "/" + travel_date[2:4]

	for airport in airport_info:
		if airport['iata'].lower() == flyingFrom.lower():
			# Get City Statuses
			city_status_source = airport_status_mapping[airport['size']]
			# Get Continents
			continent_source = airport['continent']
			# Get Country
			country_source = airport['iso']
		elif airport['iata'].lower() == flyingTo.lower():
			# Get City Statuses
			city_status_destination = airport_status_mapping[airport['size']]
			# Get Continents
			continent_destination = airport['continent']
			# Get Country
			country_destination = airport['iso']
	# International Tag
	if country_source == country_destination:
		# International flight = 1, Domestic = 0
		international = 0
	else:
		international = 1

	# Season
	if int(travel_date[:2]) == 12 and int(travel_date[3:5]) >= 15:
		season = 2
	elif int(travel_date[:2]) == 1 and int(travel_date[3:5]) <= 6:
		season = 2
	# High Season => June 15th to Aug 31
	elif int(int(travel_date[:2]) == 8 or int(travel_date[:2]) == 7 or (int(travel_date[:2]) == 6 and int(travel_date[3:5]) >= 15)):
		season = 2
	# Shoulder seasons: April 1 to Jun 14
	elif (int(travel_date[:2]) == 4 or int(travel_date[:2]) == 5) or (int(travel_date[:2]) == 6 and int(travel_date[3:5]) <= 14):
		season = 1
	# Shoulder seasons: Sept 1 to Oct 31
	elif (int(travel_date[:2]) == 9 or int(travel_date[:2]) == 10):
		season = 1
	# Low Season
	else:
		season = 0

	response = requests.get(DISTANCE_URL.format(flyingFrom, flyingTo))
	soup = BeautifulSoup(response.text, 'lxml')
	for span in soup.find_all('span'):
		if 'km' in str(span).decode('utf-8') and 'row_odd_font' in str(span).decode('utf-8'):
			distance = str(span).replace('<span class="row_odd_font">', '').replace('</span>', '').strip()
			distance = distance.replace('km', '').strip()
			break


	for booking_date in date_ranges:
		prediction_input['instances'].append(
						{"arrival": flyingTo.upper(),
						"distance": float(distance),
						"booking_date": booking_date,
						"city_status_destination": city_status_destination,
						# Need input from shah
						"direct": 0,
						"continent_source": continent_source,
						"departure": flyingFrom.upper(),
						# delete in future
						"stops": 0,
						"city_status_source": city_status_source,
						"country_source": country_source,
						"season": season,
						"continent_destination": continent_destination,
						"country_destination": country_destination,
						# delete in the future
						"airline": 'Air Canada Rouge',
						# delete in future
						"nb_flights_offered": 35,
						"international": international,
						"travel_date": travel_date,
						# delete in future
						"month_of_travel": int(travel_date[0:2]),
						"days_until_departure": calculate_date_difference_diff(booking_date,travel_date)})
	return prediction_input

@csrf_exempt 
def index(request):
	if request.method == "POST":
		
		flight_input = request.body.split("&")
		for input_data in flight_input:
			if 'flyingFrom' in input_data:
				flyingFrom = input_data.replace('flyingFrom=','')
			elif 'flyingTo' in input_data:
				flyingTo = input_data.replace('flyingTo=','')
			elif 'dateFrom' in input_data:
				dateFrom = input_data.replace('dateFrom=','')
			elif 'dateTo' in input_data:
				dateTo = input_data.replace('dateTo=','')
		flight_request_input = get_flight_input(flyingFrom, flyingTo, dateFrom, dateTo)		
		json_response = predict_json(project_name, model_name, flight_request_input, version_name)
		return JsonResponse(json_response, safe=False)
	else:
		return HttpResponse("Hello, world. You're at the polls index.")

# @csrf_exempt
# class MyView(View):
#     def get(self, request, *args, **kwargs):
#         return HttpResponse('This is GET request')

#     def post(self, request, *args, **kwargs):
#         return HttpResponse('This is POST request')


		



  