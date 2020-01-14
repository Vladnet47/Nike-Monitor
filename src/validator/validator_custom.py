# -*- coding: utf-8 -*-
import os
import psycopg2

# Returns true if product should be send to notification module
def shouldNotify(product, databaseConnection):
    if product is None or 'id' not in product:
        print("No valid product")
        return

    id = product['id']

    # For each product not in database, add it to the list of notifications
    if not productExistsInDatabase(id, databaseConnection):
        addProductIdToDatabase(id, databaseConnection)
        return True

    return False

# Returns true if product id already exists in database
def productExistsInDatabase(id, databaseConnection):
    idExists = False

    try:
        cursor = databaseConnection.cursor()
        cursor.execute('SELECT EXISTS (SELECT "ID" FROM "ID" WHERE "ID"=%(id)s)', { 'id': id })

        idExists = cursor.fetchone()[0]

        databaseConnection.commit()
        cursor.close()
    except (Exception, psycopg2.DatabaseError) as error:
        print("Failed to check if product id exists with error:")
        print(error)
    
    return idExists

# Adds product id to database
def addProductIdToDatabase(id, databaseConnection):
    try:
        cursor = databaseConnection.cursor()
        cursor.execute('INSERT INTO "ID" VALUES (%(id)s)', {'id': id})
        databaseConnection.commit()
        cursor.close()
    except (Exception, psycopg2.DatabaseError) as error:
        print("Failed to store product id with error:")
        print(error)