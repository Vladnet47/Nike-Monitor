# -*- coding: utf-8 -*-
import os
import requests
import psycopg2
import json
import pika
import notifier_custom

def main():
    readFromPipeline()

# Opens connection to pipeline and reads messages from incoming queue
def readFromPipeline():
    # Read name of queue from environment variable
    queue = os.getenv('INCOMING_QUEUE')
    if queue is None:
        print("Must specify incoming queue as environment variable INCOMING_QUEUE")
        return

    # Connect to pipeline
    pipelineConnection = pika.BlockingConnection(pika.ConnectionParameters(host = os.getenv('PIPELINE_HOST', 'localhost')))
    channel = pipelineConnection.channel()

    print("Connected to pipeline and " + queue + " queue, waiting for data...")

    # Create a persistent queue. If it already exists, this will not create another one
    channel.queue_declare(queue = queue, durable = True)

    # Only receive new message when finished with previous one
    channel.basic_qos(prefetch_count = 1)
    channel.basic_consume(queue = queue, on_message_callback = callback)
    
    # Enter never ending loop, waiting for messages
    channel.start_consuming()

# Callback function for when message arrives in incoming queue
def callback(ch, method, properties, body):
    print("Received data from pipeline")
    databaseConnection = connectToDatabase()

    webHookUrls = getWebHooksFromDatabase(databaseConnection)
    if webHookUrls is None:
        print("Unable to retrieve webhook urls from database, or none found")
    
    # Extract data from pipeline body
    product = json.loads(body)
    if product is None:
        print("Empty product in pipeline")

    # Get notification for discord
    discordData = notifier_custom.getDiscordNotification(product)
    if discordData is not None:
        serializedData = json.dumps(discordData)

        # Send formatted notification to all webhooks in database
        for webHookUrl in webHookUrls:
            print("Posting notification to " + webHookUrl)
            sendToWebhook(webHookUrl, serializedData)

    if databaseConnection is not None:
        databaseConnection.close()
        print("Disconnected from database")

    # Acknowledge receipt of data
    ch.basic_ack(delivery_tag = method.delivery_tag)

# Connects to postgres database
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

# Returns list of all webhooks in database
def getWebHooksFromDatabase(databaseConnection):
    if databaseConnection is None:
        return

    webHookList = []

    try:
        cursor = databaseConnection.cursor()
        cursor.execute('SELECT * FROM "WebHooks"')
        rows = cursor.fetchall()
        databaseConnection.commit()
        cursor.close()

        for row in rows:
            webHookList.append(str(row[0]))
    except (Exception, psycopg2.DatabaseError) as error:
        print("Failed to retrieve webhook urls from database with error:")
        print(error)
    
    return webHookList
        
def sendToWebhook(webhookUrl, data):
    try:
        response = requests.post(webhookUrl, data = data, headers = {'Content-Type': 'application/json'})
        if response.status_code == 429:
            print("Sent too many requests to webhook")
        elif response.status_code != 204:
            print("Failed to post to webhook")
    except HttpError as error:
        print("Failed to post to webhook with error:")
        print(error)

main()