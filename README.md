# Flight crawler
Python script crawling for flights


This is a python script crawling a remote web service to find flights and related prices.
At the end of elaboration it sends a summary email to a given address.

## Notes: 
*	it reads a file provided by http://openflights.org/data.html with all IATA codes.
*	The file must be in the same directory of script.
*	You need to configure a mailbox recipient that is the sender of the final message.
*	If you want to filter for a restricted list of airports, you need to edit the airports.csv file.
*	The script queries the web service with an offset of +\\- 3 days for both departure and return date.
*	The result is an html file with a list of options: the one highlighted in green is the cheapest one, while the one highlighted in yellow is the one that exactly matches queried dates

## Usage example:

A specific destination:

`python flights_crawler.py 20160201 20160210 JFK LAX`

All destinations in file:

`python flights_crawler.py 20160201 20160210 JFK all`

