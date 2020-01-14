import os
from flask import Flask, request
from flask_restful import Resource, Api, reqparse
import psycopg2
import json
from datetime import datetime

app = Flask(__name__)
api = Api(app)

# Accepts data from weather station and inserts it into database
class WebhookManagement(Resource):
    # Adds specified webhooks to database
    # POST body must be a JSON webhooks=[webhook1, webhook2, ... ]
    def post(self):
        # Parse webhooks from form and verify that they exist
        rawWebhooks = request.form.get('webhooks', None)
        webhooks = parseWebhookList(rawWebhooks)
        if webhooks is None:
            return "Request must contain 'webhooks' array in body.", 400 # Bad Request

        # Connect to database
        databaseConnection = connectToDatabase()
        if databaseConnection is None:
            return "Unable to connect to database.", 500 # Internal server error

        # Delete all webhooks from database
        for webhook in webhooks:
            if not checkIfWebhookExists(webhook, databaseConnection):
                insertWebhook(webhook, databaseConnection)

        # Close database connection
        if databaseConnection is not None:
            databaseConnection.close()
            print("Database connection closed")

        return 200

    # Deletes specified webhooks from the database
    # DELETE url should be http://host:port/webhook?webhook[]=webhook1&webhook[]=webhook2 ...
    def delete(self):
        # Parse arguments from the request
        parser = reqparse.RequestParser()
        parser.add_argument('webhooks', action='append')
        args = parser.parse_args()
        rawWebhooks = args['webhooks'][0]

        # Verify that webhooks exist
        webhooks = parseWebhookList(rawWebhooks)
        if webhooks is None:
            return "Request must contain 'webhooks' array in url.", 400 # Bad Request

        # Connect to database
        databaseConnection = connectToDatabase()
        if databaseConnection is None:
            return "Unable to connect to database.", 500 # Internal server error

        # Delete all specified webhooks from database
        for webhook in webhooks:
            removeWebhook(webhook, databaseConnection)

        # Close database connection
        if databaseConnection is not None:
            databaseConnection.close()
            print("Database connection closed")

        return 200

# Test method to make sure client is able to connect to API
class Ping(Resource):
    def get(self):
        return 200 # ok

# Test method to make sure services are running
class Help(Resource):
    def get(self):
        databaseConnection = connectToDatabase()
        if databaseConnection is None:
            return "Unable to connect to database.", 500 # Internal server error
        else:
            databaseConnection.close()
            print("Database connection closed")

        return 200

# Validates request attributes and types
def parseWebhookList(rawWebhooks):
    # Check if request contains webhooks attribute
    if rawWebhooks is None:
        print("Webhooks attribute not included in request")
        return None
    
    # Decode JSON from request to get webhooks
    try:
        rawWebhooks = json.loads(rawWebhooks)
    except json.JSONDecodeError as error:
        print("Unable to decode JSON from request")
        return None

    # Check if webhooks is an array
    if not isinstance(rawWebhooks, list):
        print("Webhooks attribute is not of type list")
        return None

    return rawWebhooks

# Returns true if specified webhook already exists, false otherwise
def checkIfWebhookExists(webhook, databaseConnection):
    if webhook is not None:
        try:
            cursor = databaseConnection.cursor()
            cursor.execute('SELECT EXISTS (SELECT "Discord" FROM "WebHooks" WHERE "Discord"=%(webhook)s)', { 'webhook': webhook })
            if cursor.fetchone()[0]:
                print("Webhook exists in database")
                return True
            else:
                print("Webhook does not exist in database")

            databaseConnection.commit()
            cursor.close()
        except (Exception, psycopg2.DatabaseError) as error:
            print("Failed to check if webhook exists")
            print(error)

    return False

# Inserts specified webhook into the database
def insertWebhook(webhook, databaseConnection):
    if webhook is not None:
        try:
            cursor = databaseConnection.cursor()
            cursor.execute('INSERT INTO "WebHooks" VALUES (%(webhook)s)', { 'webhook': webhook })

            databaseConnection.commit()
            cursor.close()

            print("Inserted webhook " + webhook)
        except (Exception, psycopg2.DatabaseError) as error:
            print("Failed to insert webhook")
            print(error)

# Removes specified webhook from the database
def removeWebhook(webhook, databaseConnection):
    if webhook is not None:
        try:
            cursor = databaseConnection.cursor()
            cursor.execute('DELETE FROM "WebHooks" WHERE "Discord"=%(webhook)s', { 'webhook': webhook })

            databaseConnection.commit()
            cursor.close()

            print("Removed webhook " + webhook)
        except (Exception, psycopg2.DatabaseError) as error:
            print("Failed to remove webhook")
            print(error)

# Connects to postgres database and returns connection object
def connectToDatabase():
    connection = None

    try:
        connection = psycopg2.connect(
            host=os.getenv('DATABASE_HOST', 'localhost'), 
            database=os.getenv('DATABASE_NAME'), 
            user=os.getenv('DATABASE_USER', 'postgres'), 
            password=os.getenv('DATABASE_PASSWORD', 'postgres'), 
            port=os.getenv('DATABASE_PORT', '5432')
        )

        # Print database properties
        if connection is not None:
            print("Connected to database")

    except (Exception, psycopg2.OperationalError) as error:
        print("Failed to connect to database with error:")
        print(error)

    return connection

# Specify urls for API endpoints
api.add_resource(WebhookManagement, '/webhooks')
api.add_resource(Ping, '/ping')
api.add_resource(Help, '/help')

if __name__ == '__main__':
    app.run(host=os.getenv('HOST', '0.0.0.0'), port=os.getenv('PORT', '80'))