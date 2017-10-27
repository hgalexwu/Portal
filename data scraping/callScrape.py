import scrape
import json
import datetime
import os
from datetime import date, timedelta
# list of source and destination airports
sources = ("nyc","mia","yul")
destinations = ("nyc","mia","yul")


def everyDay(startDate, day_range):
	everyDay = []
	for i in range(day_range):
		startDate += datetime.timedelta(days=1)
		everyDay.append(date.strftime(startDate, '%m/%d/%y'))
	return everyDay

# create directory to store json if not already existed
directory = "Scrape on "+str(datetime.date.today()) 
if not os.path.exists(directory):
	os.makedirs(directory)

for source in sources:
	for destination in destinations:
		for date in everyDay(date.today(), 180):
			if (source != destination):
				scraped_data = scrape.parse(source,destination,date)
				file_name = directory+'/%s-%s-%s-flight-results.json'%(date.replace('/',''),source,destination)
				print ("Writing data to output file: ", file_name)
				with open(file_name,'w') as fp:
				 	json.dump(scraped_data,fp,indent = 4)