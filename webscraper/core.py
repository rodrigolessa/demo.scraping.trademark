# Sample:
# create a concatenated string from 0 to 19 (e.g. "012..1819")
# nums = [str(n) for n in range(20)]
# print "".join(nums)
# much more efficient then: nums += str(n)
# Best
# nums = map(str, range(20))
# print "".join(nums)

# import the necessary packages
from requests import exceptions
import argparse
import requests
#import cv2
import os
 
# Construct the argument parser and parse the arguments
ap = argparse.ArgumentParser()
ap.add_argument("-q", "--query", required=True,
	help="search query to search Bing Image API for")
ap.add_argument("-o", "--output", required=True,
	help="path to output directory of images")
args = vars(ap.parse_args())

# Microsoft Cognitive Services API key
API_KEY = "447918fee9e8438e85bf0be72b84d915"
API_KEY_2 = "b385a571dad74d45a6a49046b6a462f1"
# Maximum number of results for a given search
MAX_RESULTS = 500
# Group size for results
GROUP_SIZE = 250
 
# set the endpoint API URL
URL = "https://api.cognitive.microsoft.com/bing/v7.0/images/search"

#https://api.cognitive.microsoft.com/bing/v7.0/suggestions
#https://api.cognitive.microsoft.com/bing/v7.0/entities
#https://api.cognitive.microsoft.com/bing/v7.0/images
#https://api.cognitive.microsoft.com/bing/v7.0/news
#https://api.cognitive.microsoft.com/bing/v7.0/spellcheck
#https://api.cognitive.microsoft.com/bing/v7.0/videos
#https://api.cognitive.microsoft.com/bing/v7.0/images/visualsearch
#https://api.cognitive.microsoft.com/bing/v7.0

# When attempting to download images from the web both the Python
# programming language and the requests library have a number of
# exceptions that can be thrown so let's build a list of them now
# so we can filter on them
EXCEPTIONS = set([IOError, FileNotFoundError,
	exceptions.RequestException, exceptions.HTTPError,
	exceptions.ConnectionError, exceptions.Timeout])

# Search term
term = args["query"]

# Headers and
headers = {"Ocp-Apim-Subscription-Key" : API_KEY}
# search parameters
params = {"q": term, "offset": 0, "count": GROUP_SIZE}
 
# Debug
print("Searching API for '{}'".format(term))

# The search
search = requests.get(URL, headers=headers, params=params)
search.raise_for_status()
 
# Grab the results from the search,
results = search.json()

# including the total number of estimated results returned by the API
estNumResults = min(results["totalEstimatedMatches"], MAX_RESULTS)

# Debug
print("{} results for '{}'".format(estNumResults, term))
 
# initialize the total number of images downloaded thus far
total = 0

# Loop over the estimated number of results in `GROUP_SIZE` groups
for offset in range(0, estNumResults, GROUP_SIZE):
	
	# Update the search parameters using the current offset
	print("Making request for group {}-{} of {}...".format(offset, offset + GROUP_SIZE, estNumResults))

	params["offset"] = offset

	# The search
	search = requests.get(URL, headers=headers, params=params)
	search.raise_for_status()
	results = search.json()
	
	print("Saving images for group {}-{} of {}...".format(offset, offset + GROUP_SIZE, estNumResults))

	# Loop over the results
	for v in results["value"]:
		# Try to download the image
		try:
			# Make a request to download
			print(" - fetching: {}".format(v["contentUrl"]))
			r = requests.get(v["contentUrl"], timeout=30)
 
			# Build the path to the output image
			ext = v["contentUrl"][v["contentUrl"].rfind("."):]
			p = os.path.sep.join([args["output"], "{}{}".format(str(total).zfill(8), ext)])
 
			# Write the image
			f = open(p, "wb")
			f.write(r.content)
			f.close()
 
		# Catch any errors
		except Exception as e:
			# check to see if our exception is in the list
			if type(e) in EXCEPTIONS:
				print(" - skipping: {}".format(v["contentUrl"]))
				continue

		# TODO: Try to load the image from disk
		# TODO: If the image is `None` then we could not properly load
		# TODO: Remove the image
 
		# Update counter
		total += 1