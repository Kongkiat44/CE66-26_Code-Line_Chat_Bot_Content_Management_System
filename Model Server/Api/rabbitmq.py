import pika
import time
import queue
from flask import jsonify

# Create a new RabbitMQ connection
def createRabbitmqConnection():

    max_retries = 30  # Maximum number of connection retries
    retry_delay = 6  # Delay between retry attempts in seconds

    for attempt in range(max_retries):
        try:
            connection = pika.BlockingConnection(pika.ConnectionParameters('rabbitmq', heartbeat=600))
            return connection
        except Exception as e:
            print(f"Failed to connect to RabbitMQ (attempt {attempt + 1}/{max_retries}): {e}")
            time.sleep(retry_delay)

    # If all retries fail, raise an exception or handle it as needed
    raise Exception("Failed to establish a connection to RabbitMQ after multiple retries")

# Check if a connection is healthy
def isConnectionHealthy(connection:pika.BlockingConnection):
    try:
        return not connection.is_closed
    except (pika.exceptions.ConnectionClosed, AttributeError):
        return False

# Get a healthy RabbitMQ connection from the pool
def getRabbitmqConnection(rabbitmq_pool:queue.Queue):
    while True:
        try:
            # Try to get a connection from the pool
            connection = rabbitmq_pool.get_nowait()

            # Check if the connection is healthy
            if isConnectionHealthy(connection):
                return connection

            # If not healthy, close the connection and remove it from the pool
            connection.close()
        except queue.Empty:
            # If the pool is empty or all connections are unhealthy, create a new connection
            return createRabbitmqConnection()

# Release a connection back to the pool
def releaseRabbitmqConnection(connection:pika.BlockingConnection, rabbitmq_pool:queue.Queue):
    rabbitmq_pool.put(connection)

# Publish message to queue
def publishToQueue(queue_name:str, rabbitmq_pool:queue.Queue, message):
    try:
        # Get a healthy RabbitMQ connection from the pool
        connection = getRabbitmqConnection(rabbitmq_pool)
        channel = connection.channel()

        # Publish the message to the RabbitMQ queue
        channel.basic_publish(exchange='', routing_key=queue_name, body=message)

        # Release the connection back to the pool
        releaseRabbitmqConnection(connection, rabbitmq_pool)

        return 'OK', 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500