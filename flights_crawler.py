# coding=utf-8
import sys
import json
import datetime
import hashlib
import requests  #pip install requests 
import argparse
import csv 
import time
from mailer.simple_mailer import Mailer
from mailer.properties import props

def buildUrlParams(dest_airport, start_airport, arrival, departure, currency, outboundFrom, outboundTo, returnFrom, returnTo):
	params = {'a': dest_airport, 'd': start_airport, 'r': arrival, 'o': departure, 'm': currency, 'bestPriceCurrency': currency, 'x': '1', 'l': 'it', 'outboundFrom': outboundFrom, 'outboundTo':outboundTo, 'returnFrom': returnFrom, 'returnTo': returnTo}
	md5 = ['f02c5a', params['d'], params['a'], params['o']]
	
	if params['r'] is not None:
		md5.append(params['r'])
	
	md5.extend([params['m'], params['l'], params['x']])
	

	if params['outboundFrom'] is not None:
		md5.append(params['outboundFrom'])
		
	
	if params['outboundTo'] is not None:
		md5.append(params['outboundTo'])

	if params['returnFrom'] is not None and params['returnTo'] is not None:
		md5.extend([params['returnFrom'], params['returnTo']])
	
	params['p'] = hashlib.md5(''.join(md5)).hexdigest()
	return params

def clean_response(resp, start_airport, dest_airport, dest_airport_ext):
	response = resp.json()
	clean_list = [x for x in response['data'] if x is not None and 'amount' in x]
	
	for x in clean_list:
		x['amount'] = int(x['amount'].replace(".", ""))
	clean_sorted_list = sorted(clean_list, key=lambda k: k['amount'])
	
	toReturn = {}
	if clean_sorted_list:
		toReturn['start_airport'] = start_airport
		toReturn['dest_airport'] = dest_airport
		toReturn['dest_airport_ext'] = dest_airport_ext
		toReturn['results'] = clean_sorted_list
	return toReturn

def generateHTMLTableFromResponse(departure, arrival,clean_sorted_list):
	
	toReturn = ''

	fromTo =  '<p>From: ' + clean_sorted_list['start_airport'] + '\tTo: ' +  clean_sorted_list['dest_airport_ext'] + '</p>'
	rows = '<table><tr><td>Dep date</td><td>Return date</td><td>Amount</td></tr>'
	
	for index, el in enumerate(clean_sorted_list['results']):
		bgcolor = 'white'

		if index == 0:
			bgcolor = '#019875'
		elif el['dep'] == departure and el['ret'] == arrival:
			bgcolor = '#FFC726'
		else:
			bgcolor = 'white'
		rows += '<tr bgcolor=' + bgcolor + ' ><td>'+ (datetime.datetime.strptime(el['dep'], dateformat)).strftime(readable_dateformat) + '</td><td>'+ (datetime.datetime.strptime(el['ret'], dateformat)).strftime(readable_dateformat) + '</td><td>'+ str(el['amount']) + '</td></tr>'
	toReturn = fromTo + rows + '</table>' 
	return toReturn

# Global vars
dateformat = '%Y%m%d'
readable_dateformat = '%Y.%m.%d'
DD = datetime.timedelta(days=3)
currency = 'EUR'

url = 'http://www.volagratis.com/capitanprice/Search'

headers = {
	'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/46.0.2490.86 Safari/537.36'
}

if __name__ == "__main__":
	
	parser = argparse.ArgumentParser()
	parser.add_argument("departure", help="Departure date")
	parser.add_argument("arrival", help="Return date")
	parser.add_argument("start_airport", help="From (airport)")
	parser.add_argument("dest_airport", help="To (airport): \n type <all> to search among all airports in the file, otherwise type IATA code. e.g. <JFK>")
	args = parser.parse_args()
	
	departure = args.departure
	arrival = args.arrival
	start_airport = args.start_airport
	dest_airport =  args.dest_airport

	outboundFrom = (datetime.datetime.strptime(departure, dateformat) - DD).strftime(dateformat)
	outboundTo = (datetime.datetime.strptime(departure, dateformat) + DD).strftime(dateformat)
	returnFrom = (datetime.datetime.strptime(arrival, dateformat) - DD).strftime(dateformat)
	returnTo = (datetime.datetime.strptime(arrival, dateformat) + DD).strftime(dateformat)
	
	
	print datetime.datetime.now(), 'Elaborating...'

	responses = []
	if dest_airport != 'all':
		
		httpParams = buildUrlParams(dest_airport, start_airport, arrival, departure, currency, outboundFrom, outboundTo, returnFrom, returnTo)
		
		resp = requests.get(url, params=httpParams, headers=headers)
		results =  clean_response(resp, start_airport, dest_airport, dest_airport)
		if results:
			responses.append(results)
	else:
		# file provided by: http://openflights.org/data.html
		#HEADER: airport_id,airport_name,city,country,iata_code,icao_code,lat,long,altitude,timezone,dst,tz
		airports_file = open("airports.csv", "rb")  #must be in same directory
		for line in csv.reader(airports_file, delimiter=','):
			#if idx % 5 == 0:
			#	time.sleep(1)
			try:
				if line[4]:
					
					httpParams = buildUrlParams(line[4], start_airport, arrival, departure, currency, outboundFrom, outboundTo, returnFrom, returnTo)
					resp = requests.get(url, params=httpParams, headers=headers)
					results =  clean_response(resp, start_airport, line[4], line[2])
					if results:
						responses.append(results)
			except Exception, e:
				print e, line, resp.text
	sorted_resps = sorted(responses, key=lambda k: k['results'][0])
	filename = str(datetime.datetime.now().strftime("%Y-%m-%d %H.%M.%S") +'_flights.html')
	f = open(filename, 'a')
	
	for x in sorted_resps:
		html = generateHTMLTableFromResponse(departure, arrival, x)
		f.write(html)
	f.close()
	
	#propes =eval(open('properties.py', 'r').read())
	mailer = Mailer(props['smtpserver'], props['port'], props['user'], props['password'], props['authenticated'])
	mailer.sendMail(props['from_addr'], props['to'], props['subject'], open(filename).read())
	print datetime.datetime.now(), 'Mail sent'
#
# URL example
#http://www.volagratis.com/capitanprice/Search?a=BUH&d=MIL&x=1&l=it&m=EUR&r=20151208&o=20151206&outboundFrom=20151203&outboundTo=20151209&returnFrom=20151205&returnTo=20151211&bestPrice=80&bestPriceCurrency=EUR&p=8760e9ac7151a7f5c197c57633a8a4ba
'''
JSON response example

"target": {"dep": "20151206", "ret": "20151208", "amount": "80", "type": 100},
"data": [
{"dep": "20151203", "ret": "20151205", "type": 400},
{"dep": "20151203", "ret": "20151206", "type": 400},
{"dep": "20151203", "ret": "20151207", "amount": "81", "type": 300},
{"dep": "20151203", "ret": "20151208", "type": 400},
{"dep": "20151203", "ret": "20151209", "amount": "90", "type": 300},
{"dep": "20151203", "ret": "20151210", "amount": "91", "type": 300},
{"dep": "20151203", "ret": "20151211", "type": 400},
{"dep": "20151204", "ret": "20151205", "amount": "120", "type": 300},
{"dep": "20151204", "ret": "20151206", "amount": "86", "type": 300},
{"dep": "20151204", "ret": "20151207", "amount": "82", "type": 300},
{"dep": "20151204", "ret": "20151208", "amount": "140", "type": 300},
{"dep": "20151204", "ret": "20151209", "amount": "80", "type": 200},
{"dep": "20151204", "ret": "20151210", "amount": "55", "type": 200},
{"dep": "20151204", "ret": "20151211", "type": 400},
{"dep": "20151205", "ret": "20151205", "amount": "338", "type": 300},
{"dep": "20151205", "ret": "20151206", "amount": "109", "type": 300},
{"dep": "20151205", "ret": "20151207", "amount": "135", "type": 300},
{"dep": "20151205", "ret": "20151208", "amount": "172", "type": 300},
{"dep": "20151205", "ret": "20151209", "type": 400},
{"dep": "20151205", "ret": "20151210", "amount": "189", "type": 300},
{"dep": "20151205", "ret": "20151211", "type": 400},
null,
{"dep": "20151206", "ret": "20151206", "amount": "60", "type": 200},
{"dep": "20151206", "ret": "20151207", "amount": "54", "type": 200},
{"dep": "20151206", "ret": "20151208", "amount": "80", "type": 100},
{"dep": "20151206", "ret": "20151209", "type": 400},
{"dep": "20151206", "ret": "20151210", "amount": "54", "type": 200},
{"dep": "20151206", "ret": "20151211", "type": 400},
null,
null,
{"dep": "20151207", "ret": "20151207", "amount": "243", "type": 300},
{"dep": "20151207", "ret": "20151208", "amount": "251", "type": 300},
{"dep": "20151207", "ret": "20151209", "amount": "35", "type": 200},
{"dep": "20151207", "ret": "20151210", "type": 400},
{"dep": "20151207", "ret": "20151211", "type": 400},
null,
null,
null,
{"dep": "20151208", "ret": "20151208", "amount": "259", "type": 300},
{"dep": "20151208", "ret": "20151209", "amount": "191", "type": 300},
{"dep": "20151208", "ret": "20151210", "type": 400},
{"dep": "20151208", "ret": "20151211", "type": 400},
null,
null,
null,
null,
{"dep": "20151209", "ret": "20151209", "amount": "386", "type": 300},
{"dep": "20151209", "ret": "20151210", "type": 400},
{"dep": "20151209", "ret": "20151211", "amount": "21", "type": 200}
]}
'''