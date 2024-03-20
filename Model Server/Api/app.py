from flask import Flask, request, jsonify
import os
import queue
from rabbitmq import createRabbitmqConnection, releaseRabbitmqConnection, publishToQueue
from waitress import serve

app = Flask(__name__)

# Get mode from env
mode = os.getenv('MODE', 'prod')

# RabbitMQ connection pool
rabbitmq_pool = queue.Queue(maxsize=10)

# Configure RabbitMQ connection
connection = createRabbitmqConnection()
channel = connection.channel()

# Delare queue, create if needed
channel.queue_declare(queue='high_priority')
channel.queue_declare(queue='medium_priority')
channel.queue_declare(queue='low_priority')

# Release the connection back to the pool
releaseRabbitmqConnection(connection, rabbitmq_pool)

@app.route('/image', methods=['POST'])
def newImage():
    name = request.get_json(force=True).get('image_name')
    group = request.get_json(force=True).get('group_id')

    if name == None or group == None:
        return 'Require image_name and group_id', 400
    
    else:
        message_dict = {
            'image_name': name,
            'group_id': group
            }
        message = jsonify(message_dict).get_data(as_text=True)
        return publishToQueue('low_priority', rabbitmq_pool, message)
    
@app.route('/graph', methods=['POST'])
def createGraph():
    user_id = request.get_json(force=True).get('user_id')
    cluster_id = request.get_json(force=True).get('cluster_id')

    if user_id == None or cluster_id == None:
        return 'Require cluster_id', 400
    
    else:
        message_dict = {
            'user_id': user_id,
            'cluster_id': cluster_id
            }
        message = jsonify(message_dict).get_data(as_text=True)
        return publishToQueue('medium_priority', rabbitmq_pool, message)

@app.route('/other', methods=['POST'])
def other():
    name = request.get_json(force=True).get('image_name')
    group = request.get_json(force=True).get('group_id')
    command = request.get_json(force=True).get('command')

    if name == None or group == None or command == None:
        return 'Require image_name, group_id and command', 400

    else:
        message_dict = {
            'image_name': name,
            'group_id': group,
            'command': command
            }
        message = jsonify(message_dict).get_data(as_text=True)
        return publishToQueue('high_priority', rabbitmq_pool,  message)

if __name__ == '__main__':
    if mode == 'dev':
        # Run with flask
        app.run(debug=True)
    else:
        # Run with waitress
        serve(app, listen='*:5000')