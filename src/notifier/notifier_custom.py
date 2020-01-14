# -*- coding: utf-8 -*-
import os
import json
from datetime import datetime
import formatNotification

def getDiscordNotification(product):
    if product is None:
        return

    if isinstance(product, str):
        print("clearing")
        return

    # Get base url for product pages
    urlBase = os.getenv('URL_BASE')
    if urlBase is None:
        print("Product url is not specified")
        return

    formatter = formatNotification.FormatNotification(formatNotification.Store.Nike)

    try:
        styleCode = product['styleCode']
        print("Formatting notification for product " + str(styleCode))
        if styleCode == '999999-999':
            styleCode = None

        # Format all attributes to be displayed
        formatter.configure(
            color = None,
            title = product['title'], 
            url = urlBase + product['url'], 
            sku = styleCode,
            imageUrl = product['image'] if 'image' in product else None, 
            publishType = product['publishType'] if 'publishType' in product else None, 
            sellDate = datetime.strptime(product['startSellDate'], '%Y-%m-%dT%H:%M:%S.%f') if 'startSellDate' in product else None, 
            price = product['price'] if 'price' in product else None
        )

        # Format how size list will be displayed
        formatter.configureSizes(
            product['sizes'] if 'sizes' in product else None,
            formatNotification.Gender.Both,
            " | "
        )
    except KeyError as missingKey:
        print("Missing key: " + str(missingKey))
        pass

    # Get discord notification and serialize it
    return formatter.getDiscordData()