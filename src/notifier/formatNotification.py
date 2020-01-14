# -*- coding: utf-8 -*-
import os
from enum import Enum
import re
import json
import requests
from datetime import datetime

# Specify which website is being parsed
class Store(Enum):
    Nike = 1

# Specify which shoe sizes to show
class Gender(Enum):
    Male = 1
    Female = 2
    Both = 3

class FormatNotification:
    # Regex expresion used to parse each product size string
    sizeParsingRegex = None

    color = None
    title = None
    url = None
    sku = None
    image = None
    publishType = None
    sellDate = None
    price = None
    sizes = None

    def __init__(self, store):
        # Must specify regex to parse size list. Regex must create groups in the form: (Male/Female/Other) (Size)
        # and must support sizes that have no gender, which automatically categorizes them as male
        if store is Store.Nike:
            # From string 'M 7 / W 6.5' creates groups (M) (7) (W) (6.5)
            # From string '12.5' creates groups () (12.5)
            self.sizeParsingRegex = r"([MW]?)[ ]?([\d]+[\.]?[\d]*)"
        else:
            self.sizeParsingRegex = None
            print("Store not specified for formatting notification")

    # Accepts all product attributes. If set to None, they will not be included in final notification
    def configure(self, color = None, title = None, url = None, sku = None, imageUrl = None, publishType = None, sellDate = None, price = None):
        # Validate and set notification parameters
        self.color = int(color) if color is not None else int(os.getenv('NOTIFICATION_DEFAULT_COLOR', "0x00ff00"))
        self.title = str(title) if title is not None else os.getenv('NOTIFICATION_DEFAULT_TITLE', "Title Unavailable")
        self.url = url if self.verifyUrl(url) else None
        self.image = imageUrl if self.verifyUrl(imageUrl, ["image/jpg", "image/jpeg", "image/png"]) else os.getenv('NOTIFICATION_DEFAULT_IMAGE')
        self.sku = sku
        self.publishType = publishType
        self.sellDate = sellDate
        self.price = price

    # Configures how list of sizes should be displayed.
    # Gender idenfies which sizes to display (Male, Female, or Both)
    # Separator string identifies how sizes should be separated in list (4 ~~ 5 ~~ 6 ...)
    def configureSizes(self, sizes, gender = None, separatorString = None):
        if sizes is None:
            self.sizes = None
            return

        # Get lists for display gender sizes
        sizesJson = self.parseSizesFromStrings(sizes)

        # Print sizes for specified gender, or just Male by default
        result = ''
        if gender is None or gender is Gender.Male:
            result += self.printSizesForGender(sizesJson["M"], "Men", separatorString)
        if gender is Gender.Female:
            result += self.printSizesForGender(sizesJson["W"], "Women", separatorString)
        if gender is Gender.Both:
            result += self.printSizesForGender(sizesJson["M"], "Men", separatorString)
            result += "\n\n"
            result += self.printSizesForGender(sizesJson["W"], "Women", separatorString)

        self.sizes = result if result else None

    def printSizesForGender(self, sizes, genderString, separatorString):
        if sizes is None or len(sizes) == 0:
            return ''

        result = genderString + "\n"

        # Read default separator if none specified
        if separatorString is None:
            separatorString = os.getenv('NOTIFICATION_DEFAULT_SIZE_SEPARATOR', ', ')

        # Print each size in list with separator in between
        result += sizes[0]
        for i in range(1, len(sizes)):
            result += separatorString
            result += sizes[i]
        
        return result

    # Returns object containing lists of sizes for each gender, parsed using regex
    def parseSizesFromStrings(self, sizes):
        result = { "M": [], "W": [] }

        if sizes is None or not isinstance(sizes, list):
            return result

        currentGender = "M"

        # Go through each string and parse it into groups
        for size in sizes:
            parsedString = re.findall(self.sizeParsingRegex, size)

            for group in parsedString:
                if group[0]:
                    currentGender = group[0]
                result[currentGender].append(group[1])

        return result

    # Returns true if url is valid, and optionally matches one of the specified formats, or False otherwise
    def verifyUrl(self, url, contentFormats = None):
        if url is not None:
            try:
                # Get headers from url and return image url if valid
                response = requests.head(url)

                if response.status_code < 400:
                    if contentFormats is None or contentFormats is not None and response.headers["content-type"] in contentFormats:
                        return True
            except HttpError as error:
                print("Invalid product url with error: ")
                print(error)

        return False

    def getDiscordData(self):
        embeds = {
            'color': self.color,
            'title': self.title,
            'footer': { 'text': 'SNKRS by NS | ' + datetime.now().strftime("%m/%d/%Y, %H:%M:%S") }
        }

        if self.url is not None:
            embeds['url'] = self.url
        
        if self.image is not None:
            embeds['thumbnail'] = { 'url': self.image, 'height': 300, 'width': 270 }

        fields = []
        if self.sku is not None:
            fields.append({ 'name': 'SKU', 'value': self.sku, 'inline': True })
        if self.sellDate is not None:
            fields.append({ 'name': 'Launch Date', 'value': self.sellDate.strftime("%m/%d/%Y, %H:%M"), 'inline': True })
        if self.publishType is not None:
            fields.append({ 'name': 'Publish Type', 'value': self.publishType, 'inline': True })
        if self.price is not None:
            fields.append({ 'name': 'Price', 'value': self.price, 'inline': True })
        if self.sizes is not None:
            fields.append({ 'name': 'Sizes', 'value': self.sizes, 'inline': True })

        embeds['fields'] = fields

        return { 'embeds': [embeds] }

    def getSlackData(self):
        return None
