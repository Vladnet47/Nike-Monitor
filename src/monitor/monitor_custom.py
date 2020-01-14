# -*- coding: utf-8 -*-
import requests
import os
import json
import time

# Reads API at specified URL and through specified Proxy (if applicable) and returns json.
# If API endpoint could not be read, returns None.
def getProductData():
    # Url defaults to None if it is not specified in environment
    url = os.getenv('TARGET_URL')
    if url is None:
        print("Please specify target url as environment variable TARGET_URL")
        return None

    headers = {
        'accept': '*/*',
        'content-type': 'application/json',
        'accept-encoding': 'gzip, deflate, br',
        'user-agent': 'SNKRS/3.14.1 (iPhone; iOS 13.1.2; Scale/3.00)',
        'accept-language': 'en-US;q=1, en-US;q=0.9',
        'Connection': 'keep-alive',
        'Cache-Control': 'no-cache',
        'Pragma': 'no-cache'
    }

    url += '&i={:1}'.format(int(time.time()))
    print("Making GET request to: " + url)

    # Make GET request to API and return None if it was unsuccessful.
    # Proxy is automatically read from HTTP_PROXY and HTTPS_PROXY environment variables if specified
    try:
        response = requests.get(url = url, headers = headers)

        if response.status_code != 200:
            return None
    except HttpError as error:
        print("Failed to make request to API with error:")
        print(error)

    return formatProductData(response.json())

# Accepts raw data from API endpoint in the form of a JSON and extracts the necessary product information.
# Returns ordered dictionary of products or None if JSON that was passed in was None.
def formatProductData(rawAPIData):
    if rawAPIData is None or 'threads' not in rawAPIData:
        return None
    
    products = []

    for thread in rawAPIData['threads']:
        product = {}

        product['id'] = thread['id']
        product['title'] = thread['seoTitle']
        product['image'] = thread['imageUrl']
        product['url'] = thread['seoSlug']

        styleCode = thread['product']['style'] + '-' + thread['product']['colorCode']
        product['styleCode'] = styleCode

        # If style code represents an actual product release
        if styleCode != '999999-999':
            product['startSellDate'] = thread['product']['startSellDate']
            product['publishType'] = thread['product']['publishType']
            product['price'] = thread['product']['price']['currentRetailPrice']
            product['sizes'] = []

            # Append all available sizes for current product into an array
            parsedSizeList = thread['product']['skus']
            for size in parsedSizeList:
                localizedSize = size['localizedSize']
                product['sizes'].append(localizedSize)

        products.append(product)

    return products