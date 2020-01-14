# -*- coding: utf-8 -*-
import os
import json
import pika
import monitor_custom
import time

def main():
    while True:
        print('Started monitoring...')

        # Retrieve product data from API
        products = monitor_custom.getProductData()

        # Send product data into pipeline to database checking module
        if products is None:
            print("Failed to format product data")
        elif len(products) == 0:
            print("No products found")
        else:
            sendToPipeline(products)

        print('Finished monitoring...')

        # Wait a specified amount of seconds (5 seconds by default)
        time.sleep(int(os.getenv('REQUEST_FREQUENCY', 5)))

# Connects to pipeline and sends each product into outgoing message queue
def sendToPipeline(products):
    if products is None:
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

    # Send each product into pipeline
    counter = 0
    for product in products:
        counter += 1
        channel.basic_publish(
            exchange = '',
            routing_key = queue,
            body = json.dumps(product),
            properties = pika.BasicProperties(
                delivery_mode = 2,  # make message persistent
            )
        )

    print("Added " + str(counter) + " products to message queue. Closing connection...")

    pipelineConnection.close()

main()