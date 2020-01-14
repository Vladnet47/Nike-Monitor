# -*- coding: utf-8 -*-
import os
import psycopg2
import pika
import json
import validator_custom

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
    print("Read product from pipeline")
    databaseConnection = connectToDatabase()

    # Extract data from pipeline body
    product = json.loads(body)
    
    if validator_custom.shouldNotify(product, databaseConnection):
        sendToPipeline(product)

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

# Connects to pipeline, serializes product data, and sends to outgoing queue
def sendToPipeline(product):
    if product is None:
        return

    queue = os.getenv('OUTGOING_QUEUE')
    if queue is None:
        print("Must specify outgoing queue as environment variable OUTGOING_QUEUE")
        return

    # Connect to pipeline
    pipelineConnection = pika.BlockingConnection(pika.ConnectionParameters(host = os.getenv('PIPELINE_HOST', 'localhost')))
    channel = pipelineConnection.channel()

    # Create a persistent queue. If it already exists, this will not create another one
    channel.queue_declare(queue = queue, durable = True)

    print("Connected to pipeline and " + queue + " queue, publishing data...")

    # Send formatted product data into pipeline
    channel.basic_publish(
        exchange = '',
        routing_key = queue,
        body = json.dumps(product),
        properties = pika.BasicProperties(
            delivery_mode = 2,  # make message persistent
        )
    )

    print("Published product to message queue. Closing connection...")

    pipelineConnection.close()

main()